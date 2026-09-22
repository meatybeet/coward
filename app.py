import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
from uuid import uuid4

import boto3
import redis
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from pymongo import DESCENDING, MongoClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://127.0.0.1:27017")
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
BUCKET = "images"
MAX_UPLOAD_BYTES = 2 * 1024 * 1024

mongo = MongoClient(MONGO_URL, serverSelectionTimeoutMS=1_000)
database = mongo.gallery
cache = redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1)
s3 = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    region_name="us-east-1",
    config=Config(signature_version="s3v4"),
)


def wait_for_dependencies() -> None:
    last_error: Exception | None = None
    for _ in range(30):
        try:
            mongo.admin.command("ping")
            cache.ping()
            s3.head_bucket(Bucket=BUCKET)
            return
        except ClientError as error:
            if error.response["Error"].get("Code") in {"404", "NoSuchBucket"}:
                s3.create_bucket(Bucket=BUCKET)
                return
            last_error = error
            time.sleep(1)
        except Exception as error:
            last_error = error
            time.sleep(1)
    raise RuntimeError("MongoDB, Redis, or MinIO did not start") from last_error


@asynccontextmanager
async def lifespan(_: FastAPI):
    wait_for_dependencies()
    yield
    mongo.close()


app = FastAPI(title="WAYHOST Docker image gallery", lifespan=lifespan)


@app.get("/", include_in_schema=False)
def homepage() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    mongo.admin.command("ping")
    cache.ping()
    s3.head_bucket(Bucket=BUCKET)
    return {"status": "ok", "mongo": "ok", "redis": "ok", "minio": "ok"}


@app.get("/api/images")
def list_images() -> list[dict[str, str | int]]:
    return [
        {
            "id": item["id"],
            "name": item["name"],
            "content_type": item["content_type"],
            "size": item["size"],
            "created_at": item["created_at"].isoformat(),
        }
        for item in database.images.find({}, {"_id": 0}).sort("created_at", DESCENDING)
    ]


@app.post("/api/images", status_code=201)
async def upload_image(file: UploadFile = File(...)) -> dict[str, str | int]:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Images must be 2 MB or smaller.")

    image_id = str(uuid4())
    object_key = f"{image_id}-{file.filename or 'image'}"
    created_at = datetime.now(timezone.utc)
    s3.put_object(
        Bucket=BUCKET,
        Key=object_key,
        Body=BytesIO(content),
        ContentType=file.content_type,
    )
    document = {
        "id": image_id,
        "object_key": object_key,
        "name": file.filename or "image",
        "content_type": file.content_type,
        "size": len(content),
        "created_at": created_at,
    }
    database.images.insert_one(document)
    cache.incr("gallery:uploads")
    return {"id": image_id, "name": document["name"], "size": len(content)}


@app.get("/api/images/{image_id}")
def read_image(image_id: str) -> StreamingResponse:
    item = database.images.find_one({"id": image_id})
    if item is None:
        raise HTTPException(status_code=404, detail="Image not found.")

    object_response = s3.get_object(Bucket=BUCKET, Key=item["object_key"])

    def stream():
        try:
            yield from object_response["Body"].iter_chunks(chunk_size=64 * 1024)
        finally:
            object_response["Body"].close()

    return StreamingResponse(stream(), media_type=item["content_type"])
