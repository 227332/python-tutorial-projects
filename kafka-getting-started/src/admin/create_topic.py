import argparse

from confluent_kafka.admin import AdminClient, NewTopic


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a topic")
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic name of the new topic to create",
        required=True,
    )
    parser.add_argument(
        # pylint: disable=duplicate-code
        "--port",
        type=int,
        help="Port of the Kafka broker",
        required=True,
    )
    parser.add_argument(
        "--num-partitions",
        type=int,
        help="Number of topic partitions",
        required=False,
        default=1,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    topic_name = args.topic
    port = args.port
    num_partitions = args.num_partitions

    kafka_broker = f"localhost:{port}"

    admin_client = AdminClient(
        {
            "bootstrap.servers": kafka_broker,
            "client.id": "test-admin-client",
        }
    )

    topic_list = [
        NewTopic(topic=topic_name, num_partitions=num_partitions, replication_factor=1),
    ]
    try:
        admin_client.create_topics(topic_list)
        print(f"Successfully created topic {topic_name}")
    except Exception as err:
        raise err


if __name__ == "__main__":
    main()
