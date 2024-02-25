# Getting Started with Apache Kafka

This repository sets up a Kafka cluster with a single broker and shows how to use the [confluent-kafka](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#) Python client to:
- create a new topic
- build a Kafka Producer application that sends messages to the topic
- build a Kafka Consumer application that consumes messages from the topic.

This project got inspiration from [Getting Started with Apache Kafka and Python](https://developer.confluent.io/get-started/python/).

## Prerequisites

Activate the Python version required by this project (e.g. via a Python Version Management tool like [pyenv](https://github.com/pyenv/pyenv)).

Create a Python virtual env for this project and install the project dependencies.
For example, if you use [venv](https://docs.python.org/3/library/venv.html), run:
```shell
python3 -m venv $PWD/.venv
source .venv/bin/activate
pip install .
```

For development, install dev dependencies via `pip install '.[dev]'`.

## Setting up a Kafka Cluster

We use the [official Docker image](https://docs.confluent.io/platform/current/installation/docker/installation.html) provided by Confluent. For more examples, see also their [GitHub repo](https://github.com/confluentinc/kafka-images/tree/master/examples).

Start a Docker container running a single-node Kafka cluster via the following command:
```shell
docker compose up -d
```

This command runs a Kafka cluster with a single broker and ZooKeeper as consensus manager, and sets up a Docker bridge network called kafka-getting-started_default for the communication between the broker container and the ZooKeeper container.

Note that the ZooKeeper dependency can be removed by using Kafka in KRaft mode. 
A docker compose file setting up a Kafka cluster in KRaft mode would look like the following:
```yaml
services:
  kafka:
    image: confluentinc/cp-kafka:7.6.0
    hostname: kafka
    ports:
      - 9092:9092
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,LISTENER_INTERNAL:PLAINTEXT,LISTENER_HOST:PLAINTEXT'
      # listeners that clients will use to connect to the broker
      KAFKA_ADVERTISED_LISTENERS: 'LISTENER_INTERNAL://kafka:29092,LISTENER_HOST://localhost:9092'
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka:29093'
      # listeners that Kafka binds to
      # unlike for advertised listeners, replace localhost here with 0.0.0.0
      KAFKA_LISTENERS: 'CONTROLLER://kafka:29093,LISTENER_INTERNAL://kafka:29092,LISTENER_HOST://0.0.0.0:9092'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'LISTENER_INTERNAL'
      # set it to a base64-encoded UUID
      # (e.g. run: cat /proc/sys/kernel/random/uuid | tr -d '-' | base64 | cut -b 1-22)
      CLUSTER_ID: 'MjA3ODcyMTVhNTY3NDM3NG'
```
However, be aware that Kafka KRaft is a recent functionality and is currently not working as expected on this project: it doesn't recognize the topic requested by the Consumer application and so it attempts to create a new topic.

This project will keep using ZooKeeper for now and will migrate to Kafka KRaft once it becomes more mature.

## Creating a Kafka topic

Activate the python environment.

Check the command to create a new topic:
```shell
python src/admin/create_topic.py [--help]
```

Example:
```shell
python src/admin/create_topic.py --topic test-topic --port 9092
```

## Producing messages to the Kafka topic

Activate the python environment.

Check the command to produce N messages:
```shell
python src/producer/main.py [--help]
```

Example:
```shell
python src/producer/main.py --topic test-topic --port 9092
```

You can quickly check that the producer application has correctly sent the messages to the Kafka topic by using the [kcat](https://docs.confluent.io/platform/current/tools/kafkacat-usage.html) utility:
```shell
# option 1: running kcat on the same Docker bridge network
docker run -it --network=kafka-getting-started_default edenhill/kcat:1.7.1 -b kafka:29092 -t test-topic

# option 2: running kcat on the Docker host network
docker run -it --network=host edenhill/kcat:1.7.1 -b localhost:9092 -t test-topic
```

## Consuming messages from the Kafka topic

Activate the python environment.

Check the command to consume messages:
```shell
python src/consumer/main.py [--help]
```

You can choose weather to start from the latest committed offset or whether to run in replay mode.
In case of replay, you have to provide the range [start offset, end offset] of offsets you would like to replay.

Example:
```shell
python src/consumer/main.py --topic test-topic --port 9092 [replay --start-offset 0 --end-offset 3]
```

## Clean-up

Deactivate your virtual env. 
If you created it via [venv](https://docs.python.org/3/library/venv.html), run:
```shell
deactivate
```

Stop Docker containers:
```shell
docker compose stop
```

If you want to stop and remove containers and networks, run:
```shell
docker compose down
```
