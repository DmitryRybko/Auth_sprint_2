#!/usr/bin/env bash

echo "wait redis";
python3 "$PROJECT_DIR/src/utils/wait_redis.py";

echo "wait elasticsearch";
python3 "$PROJECT_DIR/src/utils/wait_elastic.py";

echo "prepare indexes in elasticsearch";
python3 "$PROJECT_DIR/src/utils/prepare_elastic_indexes.py";

echo "run fastapi project";
gunicorn src.main:app -w 4 -b :8001 -k uvicorn.workers.UvicornWorker;