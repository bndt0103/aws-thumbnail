"""S3 event -> 3 watermarked JPEGs -> DynamoDB. Execution role: existing LabRole."""

import hashlib
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import unquote_plus, unquote

import boto3
from botocore.exceptions import ClientError
from image_tools import InvalidImage, MAX_BYTES, make_thumbnails

log = logging.getLogger()
log.setLevel(logging.INFO)
s3 = boto3.client("s3")
table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
INPUT_BUCKET = os.environ["INPUT_BUCKET"]
OUTPUT_BUCKET = os.environ["OUTPUT_BUCKET"]
WATERMARK = os.environ.get("WATERMARK_TEXT", "CLOUD PHOTO")


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def emit(event, **fields):
    log.info(json.dumps({"event": event, **fields}, ensure_ascii=False))


def process_record(record):
    bucket = record["s3"]["bucket"]["name"]
    obj = record["s3"]["object"]
    key = unquote_plus(obj["key"])
    if INPUT_BUCKET == OUTPUT_BUCKET:
        raise RuntimeError("Input and output buckets must differ")
    if bucket != INPUT_BUCKET or not key.startswith("uploads/"):
        emit("SKIPPED", reason="Unexpected bucket/prefix")
        return "SKIPPED"
    # sequencer distinguishes overwrites; duplicate delivery keeps the same ID.
    revision = obj.get("versionId") or obj.get("sequencer") or obj.get("eTag")
    if not revision:
        raise ValueError("S3 event needs versionId, sequencer or eTag")
    image_id = hashlib.sha256(f"{bucket}\n{key}\n{revision}".encode()).hexdigest()[:32]
    now = int(time.time())
    token = str(uuid.uuid4())
    item = {
        "image_id": image_id,
        "source_bucket": bucket,
        "source_key": key,
        "filename": key.rsplit("/", 1)[-1],
        "created_at": timestamp(),
        "status": "PROCESSING",
        "lease_until": now + 180,
        "worker_token": token,
    }
    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(image_id) OR #s = :failed OR (#s = :processing AND lease_until < :now)",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":failed": "FAILED",
                ":processing": "PROCESSING",
                ":now": now,
            },
        )
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise
        existing = table.get_item(Key={"image_id": image_id}, ConsistentRead=True).get(
            "Item", {}
        )
        if existing.get("status") in ("COMPLETE", "REJECTED"):
            emit("DUPLICATE_SKIPPED", image_id=image_id)
            return "DUPLICATE"
        # Force Lambda async retry instead of swallowing an abandoned live lease.
        raise RuntimeError("Image already being processed; retry after lease") from exc

    started = time.perf_counter()
    try:
        get_args = {"Bucket": bucket, "Key": key}
        if obj.get("versionId"):
            get_args["VersionId"] = obj["versionId"]
        elif obj.get("eTag"):
            get_args["IfMatch"] = obj["eTag"]
        response = s3.get_object(**get_args)
        stream = response["Body"]
        try:
            if response["ContentLength"] > MAX_BYTES:
                raise InvalidImage("Image exceeds 10 MiB")
            raw = stream.read(MAX_BYTES + 1)
        finally:
            stream.close()
        item["filename"] = unquote(
            response.get("Metadata", {}).get("original-name", item["filename"])
        )[:180]
        original, thumbs = make_thumbnails(raw, WATERMARK)
        variants = []
        for thumb in thumbs:
            output_key = f"thumbnails/{image_id}/{thumb['size']}.jpg"
            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=output_key,
                Body=thumb["data"],
                ContentType="image/jpeg",
                ServerSideEncryption="AES256",
                CacheControl="private, max-age=300",
            )
            variants.append(
                {
                    "size": thumb["size"],
                    "width": thumb["width"],
                    "height": thumb["height"],
                    "bytes": len(thumb["data"]),
                    "key": output_key,
                }
            )
        item.update(
            status="COMPLETE",
            original=original,
            variants=variants,
            output_bucket=OUTPUT_BUCKET,
            watermark=WATERMARK,
            completed_at=timestamp(),
            processing_ms=int((time.perf_counter() - started) * 1000),
        )
    except InvalidImage as exc:
        item.update(status="REJECTED", error=str(exc), completed_at=timestamp())
    except Exception as exc:
        item.update(status="FAILED", error=type(exc).__name__, completed_at=timestamp())
        save_result(item, token)
        emit("FAILED", image_id=image_id, error_type=type(exc).__name__)
        raise
    save_result(item, token)
    emit(item["status"], image_id=image_id, processing_ms=item.get("processing_ms"))
    return item["status"]


def save_result(item, token):
    item.pop("lease_until", None)
    table.put_item(
        Item=item,
        ConditionExpression="worker_token = :token",
        ExpressionAttributeValues={":token": token},
    )


def lambda_handler(event, context):
    if event.get("Event") == "s3:TestEvent":
        return {"status": "TEST_EVENT_RECEIVED"}
    results, errors = [], []
    for record in event.get("Records", []):
        if record.get("eventSource") != "aws:s3" or not record.get(
            "eventName", ""
        ).startswith("ObjectCreated:"):
            continue
        try:
            results.append(process_record(record))
        except Exception as exc:
            errors.append(type(exc).__name__)
            log.exception("Record processing failed")
    if errors:
        raise RuntimeError(f"{len(errors)} record(s) failed; async retry required")
    return {"results": results}
