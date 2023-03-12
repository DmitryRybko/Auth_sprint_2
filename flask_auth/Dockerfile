FROM python:3.10-alpine

EXPOSE 8002/tcp

ARG PROJECT_DIR=/project
ENV PYTHONPATH=/project
ENV PROJECT_DIR=/project

WORKDIR "$PROJECT_DIR/flask_auth"

# Create a group and user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h "$PROJECT_DIR"

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R appuser:appgroup "$PROJECT_DIR"; chmod +x entrypoint.sh
USER appuser

ENTRYPOINT ["sh", "entrypoint.sh"]
