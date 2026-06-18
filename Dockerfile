FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD find /app -name "*.pyc" -delete && find /app -name "__pycache__" -type d -exec rm -rf {} + ; gunicorn finances_api.wsgi:application --bind 0.0.0.0:$PORT --workers 2
