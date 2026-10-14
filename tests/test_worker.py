import copy
import importlib.util
from io import BytesIO
from pathlib import Path
import sys
from unittest.mock import patch
import pytest
from PIL import Image
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/processor"))


class Table:
    def __init__(self):
        self.items = {}

    def put_item(self, Item, ConditionExpression, **kwargs):
        old = self.items.get(Item["image_id"])
        if (
            "attribute_not_exists" in ConditionExpression
            and old
            and old["status"] in ("COMPLETE", "REJECTED", "PROCESSING")
        ):
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException"}}, "PutItem"
            )
        if (
            "worker_token =" in ConditionExpression
            and old["worker_token"] != kwargs["ExpressionAttributeValues"][":token"]
        ):
            raise AssertionError("Lost worker lease")
        self.items[Item["image_id"]] = copy.deepcopy(Item)

    def get_item(self, Key, **kwargs):
        return {"Item": self.items.get(Key["image_id"], {})}


class S3:
    def __init__(self):
        buf = BytesIO()
        Image.new("RGB", (1200, 800), "blue").save(buf, "JPEG")
        self.raw, self.outputs, self.fail = buf.getvalue(), [], False

    def get_object(self, **kwargs):
        if self.fail:
            raise RuntimeError("Transient network failure")
        return {
            "Body": BytesIO(self.raw),
            "ContentLength": len(self.raw),
            "Metadata": {},
        }

    def put_object(self, **kwargs):
        self.outputs.append(kwargs)


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.setenv("INPUT_BUCKET", "input-bucket")
    monkeypatch.setenv("OUTPUT_BUCKET", "output-bucket")
    monkeypatch.setenv("TABLE_NAME", "test-table")
    s3, table = S3(), Table()
    spec = importlib.util.spec_from_file_location(
        "worker_under_test", ROOT / "src/processor/lambda_function.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch("boto3.client", return_value=s3), patch("boto3.resource") as resource:
        resource.return_value.Table.return_value = table
        spec.loader.exec_module(module)
    return module, s3, table


def event(bucket="input-bucket", key="uploads/a.jpg"):
    return {
        "Records": [
            {
                "eventSource": "aws:s3",
                "eventName": "ObjectCreated:Put",
                "s3": {
                    "bucket": {"name": bucket},
                    "object": {"key": key, "eTag": "abcd", "sequencer": "001"},
                },
            }
        ]
    }


def test_full_pipeline_and_duplicate(worker):
    module, s3, table = worker
    assert module.lambda_handler(event(), None)["results"] == ["COMPLETE"]
    assert len(s3.outputs) == 3
    item = next(iter(table.items.values()))
    assert len(item["variants"]) == 3 and item["status"] == "COMPLETE"
    assert module.lambda_handler(event(), None)["results"] == ["DUPLICATE"]
    assert len(s3.outputs) == 3 and len(table.items) == 1


def test_output_bucket_and_wrong_prefix_ignored(worker):
    module, s3, table = worker
    assert module.lambda_handler(event(bucket="output-bucket"), None)["results"] == [
        "SKIPPED"
    ]
    assert module.lambda_handler(event(key="elsewhere/a.jpg"), None)["results"] == [
        "SKIPPED"
    ]
    assert not s3.outputs and not table.items


def test_invalid_image_recorded_not_retried(worker):
    module, s3, table = worker
    s3.raw = b"fake jpg"
    assert module.lambda_handler(event(), None)["results"] == ["REJECTED"]
    assert next(iter(table.items.values()))["status"] == "REJECTED"
    assert not s3.outputs


def test_transient_failure_then_retry(worker):
    module, s3, table = worker
    s3.fail = True
    with pytest.raises(RuntimeError):
        module.lambda_handler(event(), None)
    assert next(iter(table.items.values()))["status"] == "FAILED"
    s3.fail = False
    assert module.lambda_handler(event(), None)["results"] == ["COMPLETE"]


def test_s3_test_notification(worker):
    assert (
        worker[0].lambda_handler({"Event": "s3:TestEvent"}, None)["status"]
        == "TEST_EVENT_RECEIVED"
    )
