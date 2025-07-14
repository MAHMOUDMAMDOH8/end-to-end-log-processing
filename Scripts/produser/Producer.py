from kafka import KafkaProducer
import json
import time
import logging
from logs import LogGenerator
import random
import argparse
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KafkaProducer")

TOPIC = "LogEvents"
KAFKA_BROKER = "localhost:29092"

# Initialize the log generator
log_generator = LogGenerator()

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def Stream_events(num_event=100):
    """
    Stream events to Kafka topic
    """
    counter = 0
    while counter < num_event:
        try:
            events = log_generator.generate_logs(1, interval=0)
            event = events[0]
            event_type = event['event_type']
            producer.send(TOPIC, value=event)
            logger.info(f"Produced event: {event_type}")
            counter += 1
            time.sleep(random.uniform(0.1, 0.5))
        except Exception as e:
            logger.error(f"Error producing event: {e}")
            time.sleep(1)


if __name__ == "__main__":

    # Check if Kafka is running
    if os.system("nc -z localhost 9092") != 0:
        logger.error("Kafka is not running. Please start Kafka and try again.")
        exit(1)

    Stream_events(100)
    producer.close()

