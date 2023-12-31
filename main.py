import sys
import pika
import os


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='auto_srt_pubsub', port=5672))
    channel = connection.channel()
    channel.queue_declare(queue='new_file', durable=True)

    def send_message_to_pubsub(topic, msg):
        channel.basic_publish(
            exchange='',
            routing_key='topic',
            body=msg,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            ))

    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")

        match body.type:
            case "video":
                send_message_to_pubsub("extract_sound", body.file_name)
            case "sound":
                pass
            case "srt":
                pass

    channel.basic_consume(queue='task_queue',
                          on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
