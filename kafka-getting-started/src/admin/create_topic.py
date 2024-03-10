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


def topic_exists(admin_client: AdminClient, topic_name: str) -> bool:
    metadata = admin_client.list_topics()
    for t in iter(metadata.topics.values()):
        if t.topic == topic_name:
            return True
    return False


def create_topic(
    admin_client: AdminClient, topic_name: str, num_partitions: int
) -> None:
    topic_list = [
        NewTopic(topic=topic_name, num_partitions=num_partitions, replication_factor=1),
    ]
    try:
        # asynchronously call to create topics
        # By default this operation on the broker returns immediately while
        # topics are deleted in the background, but here we give it some time (5s)
        # to propagate in the cluster before returning
        result_dict = admin_client.create_topics(topic_list, request_timeout=5.0)
    except Exception as error:
        print("Invalid operation")
        raise error

    for topic, future in result_dict.items():
        try:
            # You could pass a timeout here as well, but it is better to do it in the
            # create_topics() method so that, in case of multiple topics, we wait for
            # all futures at the same time
            future.result()  # The result itself is None
            print(f"Successfully created topic {topic}")
        except Exception as error:
            print(f"Failed to create topic {topic}: {error=}")
            raise error


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

    if not topic_exists(admin_client, topic_name):
        print(f"Topic {topic_name} does not exist. Creating it...")
        create_topic(admin_client, topic_name, num_partitions)
    else:
        print(f"Topic {topic_name} already exists, so it cannot be created again.")


if __name__ == "__main__":
    main()
