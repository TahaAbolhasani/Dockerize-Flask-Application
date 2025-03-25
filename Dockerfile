FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY app.py .

ENV METRICS_LOG_FILE=docker_system_inference_metrics.csv

EXPOSE 5000

CMD ["python", "app.py"]

