import pika, sys, os


def mq_simple(channel):
    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")

    channel.basic_consume(queue='zyd.hello', on_message_callback=callback, auto_ack=True) # 自动确认
    print(' [*] Waiting for messages. To exit press CTRL+C')


if __name__ == '__main__':
    try:
        credentials = pika.PlainCredentials('zyd_consumer', 'zyd910219')
        parameters = pika.ConnectionParameters('192.168.1.66', 5672, '/zyd', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.queue_declare(queue='zyd.hello')
        mq_simple(channel)
        channel.start_consuming()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
