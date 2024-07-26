#!/usr/bin/env python
import pika
import sys

def producer(channel):
    channel.exchange_declare(exchange='zyd.logs', exchange_type='fanout')
    message = ' '.join(sys.argv[1:]) or "info: Hello World!"
    channel.basic_publish(exchange='zyd.logs', routing_key='', body=message)
    print(f" [x] Sent {message}")

if __name__ == '__main__':
    try:
        credentials = pika.PlainCredentials('zyd', 'zyd910219')
        parameters = pika.ConnectionParameters('192.168.3.66', 5672, '/zyd', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        # channel.exchange_delete(exchange='zyd.logs') # 删除交换机
        producer(channel)
        connection.close()
    except Exception as e:
        print(str(e))
