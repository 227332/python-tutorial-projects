# Getting Started with Apache Kafka

This repository sets up a Kafka cluster with a single broker and shows how to use the [confluent-kafka](https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#) Python client to:
- create a new topic
- build a Kafka Producer application that sends messages to the topic
- build a Kafka Consumer application that consumes messages from the topic.

This project got inspiration from [Getting Started with Apache Kafka and Python](https://developer.confluent.io/get-started/python/).

## Prerequisites

Install [conflent CLI](https://docs.confluent.io/confluent-cli/current/install.html). For MacOS, you can use Homebrew:
```
brew install confluentinc/tap/cli
```

Install [Poetry](https://python-poetry.org/docs/#installation) and then create a Python virtual env for this project:
```
poetry install
```


## Setting up a Kafka Cluster

Then you can start a Docker container running a single-node Kafka cluster via the following command:
```
confluent local kafka start
```
This command sets up a Docker local network and runs the Docker image [confluentinc/confluent-local](https://hub.docker.com/r/confluentinc/confluent-local).
This image starts a Kafka cluster with a single broker and is only intended as development environment, NOT for production usage.

After the container starts running, it will print the Kafka REST Port and the Plaintext Port. 
Copy the Plaintext Port as it will be the port used by our scripts.

## Creating a Kafka topic

Activate the python environment.

Check the command to create a new topic:
```
python admin/create_topic.py [--help]
```

Example:
```
python admin/create_topic.py --topic test-topic --port 56479
```

## Producing messages to the Kafka topic

Activate the python environment.

Check the command to produce N messages:
```
python producer/main.py [--help]
```

Example:
```
python producer/main.py --topic test-topic --port 56479
```

## Consuming messages from the Kafka topic

Activate the python environment.

Check the command to consume messages:
```
python consumer/main.py [--help]
```

You can choose weather to start from the beginning or from the latest committed offset.


Example:
```
python consumer/main.py --topic test-topic --port 56479 [--replay true]
```