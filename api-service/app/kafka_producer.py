import json
import logging
from uuid import UUID
from decimal import Decimal
from kafka import KafkaProducer
from kafka.errors import KafkaError
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle UUID and other special types"""
    
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class KafkaProducerService:
    """Service for producing messages to Kafka"""
    
    def __init__(self):
        self.producer = None
        self._connect()
    
    def _connect(self):
        """Connect to Kafka broker"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v, cls=CustomJSONEncoder).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Connected to Kafka at {settings.KAFKA_BOOTSTRAP_SERVERS}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def send_embedding_request(self, message: Dict[str, Any]) -> bool:
        """
        Send embedding request to Kafka topic
        
        Args:
            message: Dictionary containing product_code, tenant_id, and data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            future = self.producer.send(settings.KAFKA_TOPIC, value=message)
            # Wait for message to be sent
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message sent to topic {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False
    
    def close(self):
        """Close Kafka producer connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")


# Global producer instance
kafka_producer = KafkaProducerService()

