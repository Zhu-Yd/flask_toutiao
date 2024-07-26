#!/usr/bin/env python
import pika
import sys

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.66'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)  # 队列进行持久化

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent  # 消息进行持久化
    ))
print(f" [x] Sent {message}")
connection.close()