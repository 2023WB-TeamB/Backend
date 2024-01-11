from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(
    env_file=os.path.join(BASE_DIR, '.env')
)
BROKER = env('RABBITMQ_BROKER')

# 기본 장고파일 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gtd.settings')
app = Celery('gtd', broker=BROKER)
app.config_from_object('django.conf:settings', namespace='CELERY')

#등록된 장고 앱 설정에서 task 불러오기
app.autodiscover_tasks()