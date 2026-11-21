FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    TZ=Europe/Zagreb \
    DB_PATH=/data/tasks.db

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY templates ./templates

EXPOSE 8080
# 2 workers is plenty for one user; SQLite WAL handles the concurrent toggle+edit.
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "2", "--access-logfile", "-", "app:app"]
