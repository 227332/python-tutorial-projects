import argparse
from collections import namedtuple
import functools

from confluent_kafka import Consumer, TopicPartition
from confluent_kafka.schema_registry.json_schema import Deserializer, JSONDeserializer
from confluent_kafka.serialization import (
    MessageField,
    SerializationContext,
    SerializationError,
)
from message_schema import dict_to_product, schema_str


Replay = namedtuple("Replay", ["start_offset", "end_offset"])


def parse_args() -> argparse.Namespace:
    main_parser = argparse.ArgumentParser(
        description=("Consume messages from the topic")
    )
    main_parser.add_argument(
        "--topic",
        type=str,
        help="Topic name to consume messages from",
        required=True,
    )
    main_parser.add_argument(
        "--port",
        type=int,
        help="Plaintext port of the Kafka broker",
        required=True,
    )
    subparsers = main_parser.add_subparsers(dest="mode", help="Mode of operation")
    replay_parser = subparsers.add_parser("replay", help="Run in replay mode")
    replay_parser.add_argument(
        "--start-offset",
        type=int,
        help="Start offset",
        required=True,
    )
    replay_parser.add_argument(
        "--end-offset",
        type=int,
        help="End offset",
        required=True,
    )
    return main_parser.parse_args()


def on_assign_callback(
    consumer: Consumer, topic_partitions: list[TopicPartition], replay: Replay
) -> None:
    if replay:
        print(f"Setting offset to {replay.start_offset} for {topic_partitions=}...")
        for topic_partition in topic_partitions:
            topic_partition.offset = replay.start_offset
        consumer.assign(topic_partitions)


def process_messages(
    consumer: Consumer,
    limit: int,
    deserializer: Deserializer,
    topic_name: str,
    fail_on_error: bool = False,
) -> None:
    counter = 0
    while (limit < 0) or (counter < limit):
        msg = consumer.poll(1.0)
        if msg is None:
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting...")
        elif msg.error():
            print(f"Error: {msg.error()=}")
        else:
            try:
                product = deserializer(
                    msg.value(), SerializationContext(topic_name, MessageField.VALUE)
                )
                print(
                    f"Consumed event from {msg.topic()=} {msg.partition()=} {msg.offset()=} "
                    f"{msg.timestamp()=}: value={product}"
                )
            except SerializationError as err:
                print(
                    f"Encountered an error for {msg.topic()=} {msg.offset()=} {msg.timestamp()=}: {err=}"
                )
                if fail_on_error:
                    raise err
            consumer.store_offsets(msg)
            counter += 1


def main() -> None:
    args = parse_args()
    print(f"Running consumer application with {args=}")

    topic_name = args.topic
    port = args.port
    replay = None
    if args.mode == "replay":
        start_offset = args.start_offset
        end_offset = args.end_offset
        assert (
            start_offset <= end_offset
        ), "Error: start offset cannot be bigger than end offset"
        replay = Replay(start_offset=start_offset, end_offset=end_offset)

    kafka_broker = f"localhost:{port}"

    # Create Consumer instance
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_broker,
            "group.id": (
                "test-normal-mode-consumer-group"
                if not replay
                else "test-replay-mode-consumer-group"
            ),
            "auto.offset.reset": "earliest",
            "enable.auto.offset.store": False,
            "enable.auto.commit": True,
            "auto.commit.interval.ms": 5000,  # default
        }
    )

    # Subscribe to topic
    consumer.subscribe(
        [topic_name],
        on_assign=functools.partial(on_assign_callback, replay=replay),
    )

    deserializer = JSONDeserializer(schema_str, from_dict=dict_to_product)

    if replay:
        num_messages = replay.end_offset - replay.start_offset + 1
        fail_on_error = True
    else:
        # consume new messages indefinitely
        num_messages = -1
        fail_on_error = False
    try:
        process_messages(
            consumer=consumer,
            limit=num_messages,
            deserializer=deserializer,
            topic_name=topic_name,
            fail_on_error=fail_on_error,
        )
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()


if __name__ == "__main__":
    main()
