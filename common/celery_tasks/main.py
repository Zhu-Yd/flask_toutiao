import os
import sys
from celery import Celery
from celery.schedules import crontab

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# 创建实例对象
celery = Celery('flask_celery')

celery.config_from_object('celery_tasks.config')

celery.autodiscover_tasks(['celery_tasks.date'])

# # 配置Celery Beat调度器
celery.conf.beat_schedule = {
    'date_pick': {
        'task': 'test.date.date_pick',
        'schedule': crontab(hour='14', minute='07', day_of_week='1-5'),
        'args': (),
    }
}

"""启动命令 (在common目录下执行)"""
# celery -A celery_tasks.main worker -l info  -P eventlet -E
# celery -A celery_tasks.main worker -l error --detach
# celery -A celery_tasks.main beat -l info
# celery -A celery_tasks.main beat -l info --detach
