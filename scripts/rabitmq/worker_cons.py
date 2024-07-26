#!/usr/bin/env python
import pika
import time

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='192.168.1.66'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)  # 队列进行持久化,生产者和消费者都需要设置
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)  # 任务处理完毕后手动确认,不确认的话会引起内存泄露


channel.basic_qos(prefetch_count=1)  # 设置预取消息的数量,处理完1个消息后再接受下一条消息，搭配ch.basic_ack 实现消息的负载均衡,降低消费者服务器压力
channel.basic_consume(queue='task_queue', on_message_callback=callback)  # 没有 auto_ack=True

channel.start_consuming()
