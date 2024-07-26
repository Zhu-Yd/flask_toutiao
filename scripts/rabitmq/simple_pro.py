import pika


def mq_simple(channel):
    channel.basic_publish(exchange='', routing_key='zyd.hello', body='Hello World!')
    print(" [x] Sent 'Hello World!'")


if __name__ == '__main__':
    credentials = pika.PlainCredentials('zyd', 'zyd910219')
    parameters = pika.ConnectionParameters('192.168.1.66', 5672, '/zyd', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    channel.queue_declare(queue='zyd.hello')
    mq_simple(channel)
    connection.close()
