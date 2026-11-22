FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY data ./data

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "invoiceflow.api:app", "--host", "0.0.0.0", "--port", "8000"]
