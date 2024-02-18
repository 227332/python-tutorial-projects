import argparse
import json
import random
import time

from confluent_kafka import Producer, KafkaError, Message
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Produce messages to send to the topic"
        )
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic name to send messages to",
        required=True,
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Plaintext port of the Kafka broker",
        required=True,
    )
    parser.add_argument(
        "--num-messages",
        type=int,
        help="Number of messages to be produced",
        required=False,
        default=10,
    )
    return parser.parse_args()

def delivery_callback(err: KafkaError, msg: Message) -> None:
    """
    Called once for each message produced to indicate delivery result.
    Invoked by poll() or flush().
    """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print(f"Produced event to topic {msg.topic()}: value = {msg.value().decode('utf-8')}")


if __name__ == "__main__":
    args = parse_args()
    topic_name = args.topic
    port = args.port
    num_messages = args.num_messages

    kafka_broker = f"localhost:{port}"

    producer = Producer({
        "bootstrap.servers": kafka_broker,
        "client.id": "test-producer",
        "acks": 1,
        "linger.ms": 0, # default, batching is disabled
    })

    products = ['book', 'alarm clock', 't-shirts', 'gift card', 'batteries']

    for _ in tqdm(range(num_messages)):
        msg_value = json.dumps({"Message": random.choice(products)}).encode('utf-8')
        producer.produce(
            topic=topic_name,
            value=msg_value,
            callback=delivery_callback,
        )
        producer.poll(0)
        # add some delay between messages
        time.sleep(random.randint(1, 10)) 

    print('Waiting for the remaining messages to be delivered...')
    producer.flush()
    print(f'Producer has completed its work.')
