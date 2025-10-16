# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /build/venv && \
    /build/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /build/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Final
from python-3.12-slim

# install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends procps && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non root user for security (UID 1000 is standard for first user on many systems)
RUN useradd -r -s /bin/bash -u 1000 appuser

WORKDIR /app

# copy virtual env from builder stage
COPY --from=builder /build/venv /app/venv

# copy application code with correct ownership and permissions
COPY --chown=appuser:appuser monitor.py .

# add venv to PA so python resolves
ENV PATH="/app/venv/bin:$PATH"

# switch to non root user
USER appuser

# healthcheck for Kubernetes liveness/readiness probes
# runs monitor with high thresholds so it should always succeed if app works
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD pthon monitor.py --cpu-threshold 100 --memory-threshold 100 || exit 1

# ENTRYPOINT is a fixed executable, CMD provides default args
ENTRYPOINT ["python", "monitor.py"]

# CMD provides default args, can be overridden at runtime
# docker run monitor:v1 --cpu-threshold 50 replaces the default args
CMD ["--cpu-threshold", "80", "--memory-threshold", "85", "--disk-threshold", "90"]
