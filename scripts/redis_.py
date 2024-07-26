from redis import StrictRedis, WatchError
from redis.sentinel import Sentinel

redis_cli = StrictRedis(host='192.168.3.66', port=6379, db=0, password='zyd910219', decode_responses=True)


# decode_responses 是否自动解码

def test_redis_conect():
    # redis_cli.set('ping', 'pong')
    res = redis_cli.get('ping')
    print(f'测试redis连接:{res}')


# redis事务 | 非事务 管道
def test_pipeline():
    pipeline = redis_cli.pipeline(transaction=False)  # 非事务管道 设置 transaction = false
    # pipeline.multi()  # 此句可省略
    pipeline.get('ping')
    pipeline.get('count')
    res = pipeline.execute()
    print(f'测试redis pipeline:{res}')


# redis 乐观锁
def test_l_lock():
    redis_cli.set('count', 10)
    try:
        pipeline = redis_cli.pipeline()
        pipeline.watch('count')
        pipeline.multi()
        pipeline.decr('count', 1)
        res = pipeline.execute()
        print(f'测试redis_l_lock:{res}')  # 测试redis_l_lock:[True]
    except WatchError as e:
        print(e)


def test_b_lock():
    redis_cli.set('count', 10)
    lock = redis_cli.setnx('count_l', 1)
    if lock:
        redis_cli.expire('count_l', 5)  # 设置自动过期时间避免死锁
        redis_cli.decr('count', 2)
        redis_cli.delete('count_l')  # 释放锁资源
    else:
        print('locked')


def test_sentinel():
    SENTINEL_HOST = [('192.168.3.66', 26380), ('192.168.3.66', 26381), ('192.168.3.66', 26382)]
    sentinel = Sentinel(SENTINEL_HOST)  # 获取哨兵
    master_name = 'mymaster'  # 主库别名
    master = sentinel.master_for(master_name, password='zyd910219', decode_responses=True)  # 获取主库实例
    slave = sentinel.slave_for(master_name, password='zyd910219', decode_responses=True)  # 获取从库实例
    master.set('master', master_name)
    res = slave.get('master')
    print(res)


if __name__ == '__main__':
    test_sentinel()
    # test_redis_conect()
    # test_b_lock()
    # test_pipeline()
