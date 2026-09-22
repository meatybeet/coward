FROM golang:1.24-bookworm AS minio-builder

ARG MINIO_VERSION=RELEASE.2025-10-15T17-29-55Z
RUN go install -v github.com/minio/minio@${MINIO_VERSION}


FROM mongo:7-jammy

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-pip redis-server ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=minio-builder /go/bin/minio /usr/local/bin/minio

RUN useradd --create-home --uid 10001 gallery

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --chown=gallery:gallery app.py entrypoint.sh ./
COPY --chown=gallery:gallery static ./static
RUN chmod 755 /app/entrypoint.sh

USER gallery

EXPOSE 8080

ENTRYPOINT ["/app/entrypoint.sh"]
