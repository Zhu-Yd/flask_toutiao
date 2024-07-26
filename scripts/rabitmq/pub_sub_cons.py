import pika

def consumer(channel):
    channel.exchange_declare(exchange='zyd.logs', exchange_type='fanout')   # 扇出交换类型

    result = channel.queue_declare(queue='', exclusive=True)    # 独占队列,会话结束自动删除队列
    queue_name = result.method.queue

    channel.queue_bind(exchange='zyd.logs', queue=queue_name)   # 绑定交换机

    print(' [*] Waiting for logs. To exit press CTRL+C')
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)


def callback(ch, method, properties, body):
    print(f" [x] {body}")


if __name__ == '__main__':
    credentials = pika.PlainCredentials('zyd_consumer', 'zyd910219')
    parameters = pika.ConnectionParameters('192.168.3.66', 5672, '/zyd', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    consumer(channel)
    channel.start_consuming()
