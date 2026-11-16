import os
from celery import Celery

# Вказуємо модуль налаштувань Django за замовчуванням
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Зчитуємо конфігурації з prefix='CELERY' із settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично шукає файли tasks.py у всіх зареєстрованих додатках з INSTALLED_APPS
app.autodiscover_tasks()