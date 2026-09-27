FROM python:3.12-slim
LABEL maintainer="Aryan Zahir" description="CSV profiling CLI tool"
RUN useradd -m -u 1000 appuser
WORKDIR /app
COPY profiler.py .
ENV PYTHONUNBUFFERED=1 LOG_LEVEL=INFO
USER appuser
VOLUME ["/data"]
ENTRYPOINT ["python", "profiler.py"]
CMD ["--input", "/data/input", "--output", "/data/output"]