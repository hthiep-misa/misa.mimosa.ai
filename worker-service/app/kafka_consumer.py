import json
import logging
import signal
import sys
from typing import List, Dict, Any
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.config import settings
from app.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class KafkaConsumerWorker:
    """Worker for consuming messages from Kafka and processing embeddings"""
    
    def __init__(self):
        self.consumer = None
        self.embedding_service = EmbeddingService()
        self.running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.warning(f"⚠️  Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _connect(self):
        """Connect to Kafka broker"""
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset=settings.KAFKA_AUTO_OFFSET_RESET,
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                max_poll_records=settings.BATCH_SIZE,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            logger.info(
                f"Connected to Kafka at {settings.KAFKA_BOOTSTRAP_SERVERS}, "
                f"topic: {settings.KAFKA_TOPIC}, "
                f"group: {settings.KAFKA_GROUP_ID}"
            )
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def process_message(self, message: Dict[str, Any]) -> bool:
        """
        Process single message
        
        Args:
            message: Message data from Kafka
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            product_code = message.get("product_code")
            tenant_id = message.get("tenant_id")
            data = message.get("data")
            metadata = message.get("metadata", {})
            
            if not all([product_code, tenant_id, data]):
                logger.warning(f"Invalid message format: {message}")
                return False
            
            logger.info(
                f"Processing message - Product: {product_code}, "
                f"Tenant: {tenant_id}, "
                f"Object: {data.get('accounting_object_code')}"
            )
            
            success = self.embedding_service.process_and_store(
                product_code=product_code,
                tenant_id=tenant_id,
                data=data,
                metadata=metadata
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    def process_batch(self, messages: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Process batch of messages
        
        Args:
            messages: List of messages to process
            
        Returns:
            Dict with processing statistics
        """
        return self.embedding_service.process_batch(messages)
    
    def start(self):
        """Start consuming messages from Kafka"""
        logger.info(f"Starting {settings.WORKER_NAME}...")
        
        # Connect to Kafka
        self._connect()
        
        self.running = True
        message_count = 0
        
        try:
            logger.info("✅ Worker is ready and waiting for messages...")
            
            while self.running:
                # Poll for messages
                message_batch = self.consumer.poll(
                    timeout_ms=settings.BATCH_TIMEOUT * 1000,
                    max_records=settings.BATCH_SIZE
                )
                
                if not message_batch:
                    continue
                
                # Process messages
                messages_to_process = []
                for topic_partition, messages in message_batch.items():
                    for message in messages:
                        messages_to_process.append(message.value)
                        message_count += 1
                
                if messages_to_process:
                    logger.info(f"📦 Processing batch of {len(messages_to_process)} messages")
                    
                    # Process batch
                    stats = self.process_batch(messages_to_process)
                    
                    logger.info(
                        f"✅ Batch processed - Success: {stats['success']}, "
                        f"Failed: {stats['failure']}, "
                        f"Total: {message_count}"
                    )
        
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
        finally:
            self.close()
    
    def close(self):
        """Close Kafka consumer connection"""
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("Kafka consumer closed")


def main():
    """Main entry point for worker"""
    # Configure logging with beautiful format
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors and better structure"""
        
        # ANSI color codes
        COLORS = {
            'DEBUG': '\033[36m',      # Cyan
            'INFO': '\033[32m',       # Green
            'WARNING': '\033[33m',    # Yellow
            'ERROR': '\033[31m',      # Red
            'CRITICAL': '\033[35m',   # Magenta
        }
        RESET = '\033[0m'
        BOLD = '\033[1m'
        DIM = '\033[2m'
        
        def format(self, record):
            # Color for log level
            levelname = record.levelname
            if levelname in self.COLORS:
                levelname_colored = f"{self.COLORS[levelname]}{self.BOLD}{levelname:8s}{self.RESET}"
            else:
                levelname_colored = f"{levelname:8s}"
            
            # Format timestamp
            timestamp = self.formatTime(record, '%Y-%m-%d %H:%M:%S')
            timestamp_colored = f"{self.DIM}{timestamp}{self.RESET}"
            
            # Format logger name
            name = record.name.split('.')[-1]  # Get last part only
            name_colored = f"{self.DIM}[{name}]{self.RESET}"
            
            # Format message
            message = record.getMessage()
            
            # Combine
            return f"{timestamp_colored} {levelname_colored} {name_colored} {message}"
    
    # Setup handler with custom formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter())
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        handlers=[handler]
    )
    
    # Print banner
    print("\n" + "=" * 80)
    print(f"🚀 {settings.WORKER_NAME.upper()}")
    print("=" * 80)
    print(f"📋 Configuration:")
    print(f"   • Kafka:  {settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"   • Topic:  {settings.KAFKA_TOPIC}")
    print(f"   • Group:  {settings.KAFKA_GROUP_ID}")
    print(f"   • Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print(f"   • Model:  {settings.EMBEDDING_MODEL}")
    print(f"   • Batch:  {settings.BATCH_SIZE} messages")
    print(f"   • Log:    {settings.LOG_LEVEL}")
    print("=" * 80 + "\n")
    
    # Create and start worker
    worker = KafkaConsumerWorker()
    
    try:
        worker.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        sys.exit(1)
    finally:
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    main()

