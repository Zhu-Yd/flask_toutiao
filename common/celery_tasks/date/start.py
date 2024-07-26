from celery_tasks.date.tasks import heart_beat

if __name__ == '__main__':
    heart_beat.delay()



