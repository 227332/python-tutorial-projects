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
docker-compose up -d
```

This command sets up a Docker bridge network and runs a Kafka cluster with a single broker and Zookeeper as consensus manager.

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

## Consuming messages from the Kafka topic

Activate the python environment.

Check the command to consume messages:
```shell
python src/consumer/main.py [--help]
```

You can choose weather to start from the beginning or from the latest committed offset.


Example:
```shell
python src/consumer/main.py --topic test-topic --port 9092 [--replay true]
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
