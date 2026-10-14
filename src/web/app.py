"""Private gallery gateway. AWS credentials remain on the server, never in JS."""

import hmac
import logging
import os
import secrets
from datetime import timedelta
from decimal import Decimal
from functools import wraps
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import check_password_hash


def plain(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, list):
        return [plain(v) for v in value]
    return value


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("APP_SECRET"),
        PASSWORD_HASH=os.environ.get("GALLERY_PASSWORD_HASH"),
        INPUT_BUCKET=os.environ.get("INPUT_BUCKET"),
        OUTPUT_BUCKET=os.environ.get("OUTPUT_BUCKET"),
        TABLE_NAME=os.environ.get("TABLE_NAME"),
        REGION=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
        MAX_CONTENT_LENGTH=11 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower()
        == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),
    )
    if test_config:
        app.config.update(test_config)
    for required in (
        "SECRET_KEY",
        "PASSWORD_HASH",
        "INPUT_BUCKET",
        "OUTPUT_BUCKET",
        "TABLE_NAME",
    ):
        if not app.config.get(required):
            raise RuntimeError(f"Missing configuration: {required}. See README.md")
    if app.config["REGION"] not in ("us-east-1", "us-west-2"):
        raise RuntimeError("Only the two course regions are allowed")
    if not app.config.get("AWS_CLIENTS"):
        aws = boto3.Session(region_name=app.config["REGION"])
        app.config["AWS_CLIENTS"] = (
            aws.client("s3", config=Config(signature_version="s3v4")),
            aws.resource("dynamodb").Table(app.config["TABLE_NAME"]),
        )
    s3, table = app.config["AWS_CLIENTS"]

    def protected(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not session.get("authenticated"):
                return jsonify(error="Vui lòng đăng nhập lại."), 401
            return fn(*args, **kwargs)

        return wrapper

    @app.before_request
    def csrf_check():
        session.setdefault("csrf", secrets.token_urlsafe(32))
        if request.method == "POST":
            supplied = request.headers.get("X-CSRF-Token") or request.form.get(
                "csrf", ""
            )
            if not hmac.compare_digest(session["csrf"], supplied):
                return (
                    jsonify(error="Phiên không hợp lệ. Tải lại trang rồi thử lại."),
                    403,
                )

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' blob: https://*.amazonaws.com; "
            "style-src 'self'; script-src 'self'; connect-src 'self'; "
            "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        return response

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            if check_password_hash(
                app.config["PASSWORD_HASH"], request.form.get("password", "")
            ):
                session.clear()
                session.update(authenticated=True, csrf=secrets.token_urlsafe(32))
                session.permanent = True
                return redirect(url_for("index"))
            error = "Mật khẩu chưa đúng."
        return render_template("login.html", error=error)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/")
    def index():
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return render_template("index.html")

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.post("/api/upload")
    @protected
    def upload():
        file = request.files.get("file")
        if not file or not file.filename:
            return jsonify(error="Hãy chọn một ảnh JPG hoặc PNG."), 400
        filename = Path(file.filename.replace("\\", "/")).name[:180]
        ext = Path(filename).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png"):
            return jsonify(error="Chỉ nhận JPG hoặc PNG."), 400
        raw = file.read(10 * 1024 * 1024 + 1)
        if not raw or len(raw) > 10 * 1024 * 1024:
            return jsonify(error="Ảnh phải lớn hơn 0 byte và không quá 10 MiB."), 400
        key = f"uploads/{uuid4().hex}{ext}"
        s3.put_object(
            Bucket=app.config["INPUT_BUCKET"],
            Key=key,
            Body=raw,
            ContentType="image/png" if ext == ".png" else "image/jpeg",
            ServerSideEncryption="AES256",
            Metadata={"original-name": quote(filename, safe="")},
        )
        return (
            jsonify(message="Đã tải lên. Hệ thống đang chờ xử lý ảnh.", source_key=key),
            202,
        )

    @app.get("/api/photos")
    @protected
    def photos():
        # Limit the scan to 1,000 records and display the 60 newest in that set.
        items, start, truncated = [], None, False
        while True:
            args = {"Limit": 100}
            if start:
                args["ExclusiveStartKey"] = start
            response = table.scan(**args)
            items.extend(response.get("Items", []))
            start = response.get("LastEvaluatedKey")
            if not start:
                break
            if len(items) >= 1000:
                truncated = True
                break
        items.sort(key=lambda item: item.get("created_at", ""), reverse=True)
        result = []
        for item in items[:60]:
            safe = {
                key: item[key]
                for key in (
                    "image_id",
                    "filename",
                    "source_key",
                    "created_at",
                    "status",
                    "original",
                    "processing_ms",
                    "error",
                )
                if key in item
            }
            safe["variants"] = []
            if item.get("status") == "COMPLETE":
                for variant in item.get("variants", []):
                    v = dict(variant)
                    v["url"] = s3.generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": app.config["OUTPUT_BUCKET"],
                            "Key": v.pop("key"),
                        },
                        ExpiresIn=300,
                    )
                    safe["variants"].append(v)
            result.append(plain(safe))
        return jsonify(items=result, truncated=truncated, displayed_limit=60)

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(error):
        return jsonify(error="Tệp quá lớn. Giới hạn ảnh là 10 MiB."), 413

    @app.errorhandler(ClientError)
    @app.errorhandler(BotoCoreError)
    def aws_error(error):
        logging.exception("AWS request failed")
        return (
            jsonify(
                error="Không kết nối được AWS. Kiểm tra phiên lab, Region và quyền role."
            ),
            503,
        )

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
