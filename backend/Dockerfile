# ── Build stage: install dependencies ────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a separate prefix so we can copy them cleanly.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages from builder.
COPY --from=builder /install /usr/local

# Copy application source.
COPY app/ ./app/

# Create the uploads directory (volume-mounted in production; pre-created here
# so the container doesn't error if no volume is attached).
RUN mkdir -p data/uploads

# Expose the port uvicorn listens on.
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
