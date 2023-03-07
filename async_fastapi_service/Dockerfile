from python:3.10-alpine

EXPOSE 8001/tcp

ARG PROJECT_DIR=/project
ENV PYTHONPATH=$PROJECT_DIR/src

WORKDIR $PROJECT_DIR

# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h "$PROJECT_DIR"

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appgroup "$PROJECT_DIR"
USER appuser

ENTRYPOINT ["gunicorn", "src.main:app", "-w 4", "-b :8001", "-k uvicorn.workers.UvicornWorker"]
