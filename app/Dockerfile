ARG PYTHON_VERSION=3.12
FROM public.ecr.aws/docker/library/python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src

# Lambda Web Adapter: same image works on Lambda Container runtime.
# It listens on AWS_LWA_PORT and forwards to the app on APP_PORT.
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.3 /lambda-adapter /opt/extensions/lambda-adapter

ENV PORT=8080 \
    AWS_LWA_PORT=8080 \
    AWS_LWA_ASYNC_INIT=true \
    AWS_LWA_INVOKE_MODE=buffered \
    AWS_LWA_READINESS_CHECK_PATH=/healthz \
    PLATFORM=unknown

EXPOSE 8080

# EC2 / Fargate path: gunicorn + uvicorn workers.
# Lambda path: the adapter runs this same command inside the container.
CMD ["gunicorn", "src.main:app", \
     "-w", "2", "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8080", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "--timeout", "30", "--graceful-timeout", "10", "--keep-alive", "5"]
