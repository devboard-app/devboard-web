FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

RUN SECRET_KEY=dummy AUTH_SERVICE_URL=dummy CORE_SERVICE_URL=dummy WORK_SERVICE_URL=dummy ANALYTICS_SERVICE_URL=dummy ATTACHMENTS_SERVICE_URL=dummy INTEGRATIONS_SERVICE_URL=dummy REDIS_URL=dummy python manage.py collectstatic --noinput

CMD ["uvicorn", "web.asgi:application", "--host", "0.0.0.0", "--port", "8000"]