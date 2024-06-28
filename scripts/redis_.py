from redis import StrictRedis

redis_cli = StrictRedis(host='192.168.1.66', port=6379, db=0, password='zyd910219', decode_responses=True)


# decode_responses 是否自动解码

def test_redis_conect():
    # redis_cli.set('ping', 'pong')
    res = redis_cli.get('ping')
    print(f'测试redis连接:{res}')


if __name__ == '__main__':
    test_redis_conect()
