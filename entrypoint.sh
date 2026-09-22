#!/bin/sh
set -eu

cleanup() {
    kill "$mongo_pid" "$redis_pid" "$minio_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM

mkdir -p /tmp/mongo /tmp/redis /tmp/minio

mongod --dbpath /tmp/mongo --bind_ip 127.0.0.1 --port 27017 \
    --logpath /tmp/mongod.log &
mongo_pid=$!

redis-server --bind 127.0.0.1 --port 6379 --save '' --appendonly no \
    --dir /tmp/redis > /tmp/redis.log 2>&1 &
redis_pid=$!

MINIO_ROOT_USER="${MINIO_ROOT_USER:-minioadmin}" \
MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-minioadmin}" \
    minio server /tmp/minio --address 127.0.0.1:9000 \
    --console-address 127.0.0.1:9001 > /tmp/minio.log 2>&1 &
minio_pid=$!

exec uvicorn app:app --host 0.0.0.0 --port 8080

