import argparse
from collections import namedtuple
import functools

from confluent_kafka import Consumer


Replay = namedtuple("Replay", ["start_offset", "end_offset"])


def parse_args():
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


def on_assign_callback(consumer, topic_partitions, replay):
    if replay:
        print(f"Setting offset to {replay.start_offset} for {topic_partitions=}...")
        for topic_partition in topic_partitions:
            topic_partition.offset = replay.start_offset
        consumer.assign(topic_partitions)


if __name__ == "__main__":
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
            "group.id": "test-consumer-group",
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

    limit = -1 if not replay else replay.end_offset - replay.start_offset + 1
    counter = 0
    # Poll for Kafka messages and print them
    try:
        while (limit < 0) or (counter < limit):
            msg = consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting...")
            elif msg.error():
                print("ERROR: %s".format(msg.error()))
            else:
                try:
                    value = msg.value().decode("utf-8")
                    print(
                        f"Consumed event from {msg.topic()=} {msg.offset()=} {msg.timestamp()=}: {value=}"
                    )
                except AttributeError as err:
                    # for a non-transient error, do not raise any exception,
                    # but log its offset together with the error, then commit the offset and
                    # proceed to the next message.
                    # After the application bug is fixed, a replay can then consume this failed msg
                    # again and process it correctly
                    print(
                        f"Encountered an error for {msg.topic()=} {msg.offset()=} {msg.timestamp()=}: {err=}"
                    )
                consumer.store_offsets(msg)
                counter += 1
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        consumer.close()
