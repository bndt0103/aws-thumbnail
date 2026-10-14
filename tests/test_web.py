from io import BytesIO
from pathlib import Path
import sys
import pytest
from werkzeug.security import generate_password_hash

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src/web"))
from app import create_app


class S3:
    def __init__(self):
        self.uploads = []

    def put_object(self, **kwargs):
        self.uploads.append(kwargs)

    def generate_presigned_url(self, *args, **kwargs):
        return "https://example.amazonaws.com/signed"


class Table:
    def scan(self, **kwargs):
        return {"Items": []}


@pytest.fixture
def client():
    s3 = S3()
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "PASSWORD_HASH": generate_password_hash("test-password"),
            "INPUT_BUCKET": "test-input",
            "OUTPUT_BUCKET": "test-output",
            "TABLE_NAME": "test-table",
            "AWS_CLIENTS": (s3, Table()),
        }
    )
    return app.test_client(), s3


def sign_in(c):
    c.get("/login")
    with c.session_transaction() as s:
        token = s["csrf"]
    assert (
        c.post("/login", data={"password": "test-password", "csrf": token}).status_code
        == 302
    )
    with c.session_transaction() as s:
        return s["csrf"]


def test_private_api_and_csrf(client):
    c, _ = client
    assert c.get("/api/photos").status_code == 401
    assert c.post("/api/upload").status_code == 403
    sign_in(c)
    assert c.get("/api/photos").json["items"] == []
    assert c.post("/api/upload").status_code == 403


def test_upload_unique_prefix_original_name_no_keys_exposed(client):
    c, s3 = client
    csrf = sign_in(c)
    for _ in range(2):
        response = c.post(
            "/api/upload",
            headers={"X-CSRF-Token": csrf},
            data={"file": (BytesIO(b"test"), "ảnh sản phẩm.jpg")},
        )
        assert response.status_code == 202
        assert "AWS_ACCESS_KEY" not in response.get_data(as_text=True)
    assert s3.uploads[0]["Key"].startswith("uploads/")
    assert s3.uploads[0]["Key"] != s3.uploads[1]["Key"]
    assert s3.uploads[0]["Metadata"]["original-name"].startswith("%")


def test_extension_rejected(client):
    c, s3 = client
    csrf = sign_in(c)
    response = c.post(
        "/api/upload",
        headers={"X-CSRF-Token": csrf},
        data={"file": (BytesIO(b"text"), "a.exe")},
    )
    assert response.status_code == 400
    assert not s3.uploads


def test_gallery_and_security_headers(client):
    c, _ = client
    sign_in(c)
    response = c.get("/")
    assert response.status_code == 200
    assert "Cloud Photo" in response.get_data(as_text=True)
    assert response.headers["X-Frame-Options"] == "DENY"
