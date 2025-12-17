FROM python:3.13 as production-stage

WORKDIR /tmp/app_build
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

COPY . ./backend/

ENV PYTHONPATH=$PYTHONPATH:/app

CMD ["gunicorn", "backend.main:app", "--workers", "1", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]