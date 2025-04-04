import json
import logging

from kafka import KafkaProducer


class ClusterKafkaProducer:
    def __init__(self, bootstrap_servers="localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=[bootstrap_servers],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        self.logger = logging.getLogger(__name__)

    def send_message(self, topic: str, message: dict):
        try:
            self.producer.send(topic, message)
            self.producer.flush()
            self.logger.info(f"Sent message to {topic}: {message}")
        except Exception as e:
            self.logger.error(f"Error sending message to {topic}: {e}")
            raise
