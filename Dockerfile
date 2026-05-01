FROM python:3.12-slim

WORKDIR /app

# Copy prompt files (read at runtime by the backend)
COPY PROMPTS/ ./PROMPTS/

# Copy frontend static files (served by FastAPI StaticFiles)
COPY frontend/ ./frontend/

# Copy backend source and dependencies
COPY backend/main.py ./backend/main.py
COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run injects PORT; default to 8080
ENV PORT=8080

EXPOSE 8080

# Run from /app so relative paths (../PROMPTS, ../frontend) in main.py resolve correctly
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
