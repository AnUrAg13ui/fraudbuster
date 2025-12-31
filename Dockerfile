# 1. Base image
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=InsuranceFraudBuster.settings
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=*
ENV DJANGO_SECRET_KEY=your-secret-key-here

# 3. Set work directory
WORKDIR /app

# 4. Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy project files
COPY . .

# 6. Run migrations and collect static files
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# 7. Expose port
EXPOSE 8000

# 8. Run the app
CMD ["gunicorn", "InsuranceFraudBuster.wsgi:application", "--bind", "0.0.0.0:8000"]
