import argparse
import functools

from confluent_kafka import OFFSET_BEGINNING, Consumer


def parse_args():
    parser = argparse.ArgumentParser(description=("Consume messages from the topic"))
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic name to consume messages from",
        required=True,
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Plaintext port of the Kafka broker",
        required=True,
    )
    parser.add_argument(
        "--replay",
        type=bool,
        help="Whether to run a full replay from the earliest offset",
        required=False,
        default=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Running consumer application with {args=}")

    topic_name = args.topic
    port = args.port
    is_replay = args.replay

    kafka_broker = f"localhost:{port}"

    # Create Consumer instance
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_broker,
            "group.id": "test-consumer-group",
            "auto.offset.reset": "earliest",
            "enable.auto.offset.store": False,
            "enable.auto.commit": True,
            "auto.commit.interval.ms": 5000,  # default
        }
    )

    def on_assign_callback(consumer, topic_partitions, is_replay):
        if is_replay:
            print(f"Resetting offset for {topic_partitions=}...")
            for topic_partition in topic_partitions:
                topic_partition.offset = OFFSET_BEGINNING
        consumer.assign(topic_partitions)

    # Subscribe to topic
    consumer.subscribe(
        [topic_name],
        on_assign=functools.partial(on_assign_callback, is_replay=is_replay),
    )

    # Poll for new messages from Kafka and print them
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                print(
                    f"Consumed event from {msg.topic()=} {msg.offset()=} {msg.timestamp()=}: value = {msg.value().decode('utf-8')}"
                )
                consumer.store_offsets(msg)
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
