FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt python-telegram-bot python-dotenv

COPY main.py .

CMD ["python", "main.py"]
