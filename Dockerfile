FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy API source code
COPY . .

# Cloud Run sets $PORT automatically. Default 8080 for local Docker.
ENV PORT=8080

# Run FastAPI with Uvicorn using the $PORT variable
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]