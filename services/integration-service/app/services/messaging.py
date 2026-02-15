import json
from confluent_kafka import Producer

from app.core.config import settings


class MessagingService:
    def __init__(self) -> None:
        self.producer = Producer({"bootstrap.servers": settings.kafka_bootstrap_servers})

    def publish(self, topic: str, key: str, value: dict) -> None:
        self.producer.produce(topic=topic, key=key, value=json.dumps(value))
        self.producer.flush(timeout=5)
