from celery_tasks.main import celery
from datetime import datetime
import time


@celery.task(bind=True, name='test.date.heart_beat')  # bind=true 将自身绑定到函数
def heart_beat(self):
    while True:
        now = datetime.now()
        if now.hour in [10, 11] and now.minute == 35:
            date_pick.delay()
        if now.hour in [14, 15] and now.minute == 5:
            date_pick.delay()
        print('心跳:{}:{}:{}'.format(now.hour, now.minute, now.second))

        self.update_state(state='PROGRESS')
        time.sleep(30)


@celery.task(name='test.date.date_pick')
def date_pick():
    print(f'当前时间为:{datetime.utcnow()}')


if __name__ == '__main__':
    print("执行完毕")
