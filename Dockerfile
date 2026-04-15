# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src/ ./src/
COPY .env .env

RUN mkdir -p /app/data

ENV PYTHONPATH=/app/src

CMD ["python", "src/main.py"]
