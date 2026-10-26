FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY tests/ ./tests/
COPY specs/ ./specs/
COPY CONTEXT_RULES.md ./CONTEXT_RULES.md
COPY README.md ./README.md

CMD ["python", "-m", "pytest", "tests/test_harness.py", "-v"]
