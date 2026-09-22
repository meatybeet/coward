# Docker image gallery

This is a full-stack smoke test for a WAYHOST Docker site.  One public Docker
image starts:

- FastAPI and the browser gallery on port `8080`;
- MongoDB for image metadata;
- Redis for an upload counter; and
- MinIO for image objects.

It is deliberately a **test application**, not a production deployment
pattern. WAYHOST Docker sites run one read-only container without volumes, so
the MongoDB, Redis, and MinIO data lives under `/tmp` and is lost if the
container restarts or the site is redeployed. For production, use external
managed MongoDB, Redis, and object storage.

## Build and publish

From this directory, replace `YOUR_DOCKERHUB_USER` with a Docker Hub namespace
you control:

```sh
docker build -t YOUR_DOCKERHUB_USER/wayhost-image-gallery:0.1 .
docker push YOUR_DOCKERHUB_USER/wayhost-image-gallery:0.1
```

The image must be public, because the hosting service does not receive Docker
registry credentials.

The Docker build compiles MinIO from its public source release, since MinIO no
longer publishes a community Docker image or a stable prebuilt download.

## Test locally with the WAYHOST constraints

```sh
docker run --rm -p 8080:8080 \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m \
  --tmpfs /run:rw,noexec,nosuid,size=16m \
  --memory=512m --memory-swap=512m --cpus=1.0 --pids-limit=100 \
  --cap-drop=ALL --security-opt=no-new-privileges \
  YOUR_DOCKERHUB_USER/wayhost-image-gallery:0.1
```

Open `http://localhost:8080`, upload a small image (up to 2 MB), then verify
that its thumbnail appears. `http://localhost:8080/api/health` should return
`mongo`, `redis`, and `minio` as `ok`.

## Deploy through the panel

Create a **Docker** site on a dedicated-hosting account and enter:

| Panel field | Value |
| --- | --- |
| Image | `YOUR_DOCKERHUB_USER/wayhost-image-gallery:0.1` |
| Container port | `8080` |
| Environment | Leave empty |

After the site is ready, open the generated hostname over HTTP (or enable TLS
and use HTTPS). Uploading and viewing an image verifies the reverse proxy,
FastAPI, MongoDB, Redis, and MinIO in the same running Docker site.

The MinIO console is intentionally not exposed: a WAYHOST Docker site publishes
only the configured application port.
