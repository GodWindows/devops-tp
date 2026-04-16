FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies for the FastAPI app
RUN pip install --no-cache-dir fastapi uvicorn

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
