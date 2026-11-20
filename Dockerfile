FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY adapters/ adapters/
COPY commands/ commands/
COPY services/ services/

CMD ["python", "main.py"]