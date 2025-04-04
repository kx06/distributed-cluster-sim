import json
import logging

from kafka import KafkaConsumer


class ClusterKafkaConsumer:
    def __init__(self, topic: str, bootstrap_servers="localhost:9092"):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=[bootstrap_servers],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            group_id="cluster-group",
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        )
        self.logger = logging.getLogger(__name__)

    def consume_messages(self):
        self.logger.info(f"Starting to consume messages from topic")
        for message in self.consumer:
            self.logger.info(f"Received message: {message.value}")
            yield message.value
