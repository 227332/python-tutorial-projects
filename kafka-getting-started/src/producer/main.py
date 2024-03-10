import argparse
import random
import time

from confluent_kafka import KafkaError, Message, Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import MessageField, SerializationContext
from message_schema import Product, product_to_dict, schema_str
from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Produce messages to send to the topic")
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
        help="Port of the Kafka broker",
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
        print(f"Message delivery failed: {err=}")
    else:
        # msg.value() is a byte-representation of a json-serialized object
        print(
            f"Produced event to {msg.topic()=} {msg.partition()=} {msg.offset()=} "
            f"{msg.timestamp()=}: value = {msg.value().decode('utf-8')}"
        )


def main() -> None:
    args = parse_args()
    topic_name = args.topic
    port = args.port
    num_messages = args.num_messages

    kafka_broker = f"localhost:{port}"

    producer = Producer(
        {
            "bootstrap.servers": kafka_broker,
            "client.id": "test-producer",
            "acks": 1,
            "linger.ms": 0,  # default, batching is disabled
        }
    )

    schema_registry_client = SchemaRegistryClient(
        {
            "url": "http://localhost:8081",
        }
    )

    json_serializer = JSONSerializer(
        schema_str=schema_str,
        schema_registry_client=schema_registry_client,
        to_dict=product_to_dict,
    )

    product_names = ["book", "alarm clock", "t-shirts", "gift card", "batteries"]

    for _ in tqdm(range(num_messages)):
        product = Product(product_name=random.choice(product_names))
        msg_value = json_serializer(
            product, SerializationContext(topic_name, MessageField.VALUE)
        )
        producer.produce(
            topic=topic_name,
            value=msg_value,
            callback=delivery_callback,
        )
        producer.poll(0)
        # add some delay between messages
        time.sleep(random.randint(1, 10))

    print("Waiting for the remaining messages to be delivered...")
    producer.flush()
    print("Producer has completed its work.")


if __name__ == "__main__":
    main()
