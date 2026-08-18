FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english', device=-1)"
ENV METRICS_LOG_FILE=docker_system_inference_metrics.csv
EXPOSE 5000
CMD ["python", "app.py"]
