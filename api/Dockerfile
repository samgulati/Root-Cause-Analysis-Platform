FROM python:3.10-slim

WORKDIR /app

# Install system deps (optional but safe)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY api/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy API + engine
COPY api ./api
COPY rca_engine ./rca_engine

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
