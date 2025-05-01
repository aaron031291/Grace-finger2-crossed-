# communications_mesh/protocols/transport.py

import time
import uuid
import logging
from typing import Dict, Optional
from prometheus_client import Counter, Histogram, Gauge
from circuitbreaker import circuit
from dataclasses import dataclass
import threading
import json
from cryptography.fernet import Fernet
import hashlib
import hmac

# Metrics
TRANSPORT_LATENCY = Histogram('transport_latency_seconds', 'Message delivery latency', ['protocol'])
TRANSPORT_SUCCESS = Counter('transport_success_total', 'Successful deliveries', ['protocol'])
TRANSPORT_FAILURE = Counter('transport_failure_total', 'Delivery failures', ['protocol', 'error_type'])
TRANSPORT_QUEUE = Gauge('transport_queue_size', 'Current message queue size')

# Security
class MessageSigner:
    def __init__(self, secret_key: str):
        self.key = secret_key.encode()
        
    def generate_signature(self, message: str) -> str:
        return hmac.new(self.key, message.encode(), hashlib.sha256).hexdigest()
    
    def verify_signature(self, message: str, signature: str) -> bool:
        expected = self.generate_signature(message)
        return hmac.compare_digest(expected, signature)

@dataclass
class TransportConfig:
    max_retries: int = 3
    base_timeout: float = 1.0
    backoff_factor: float = 2.0
    max_payload_size: int = 1024 * 1024  # 1MB
    encryption_key: Optional[str] = None

class MessagePacket:
    def __init__(self, 
                 sender: str, 
                 recipient: str, 
                 payload: Dict,
                 protocol: str = "mesh.v2",
                 signer: Optional[MessageSigner] = None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.recipient = recipient
        self.timestamp = time.time()
        self.protocol = protocol
        self.payload = self._encrypt_payload(payload)
        self.signature = self._sign_message(signer) if signer else None

    def _encrypt_payload(self, payload: Dict) -> bytes:
        """Encrypt payload if encryption key is configured"""
        if not TransportManager.config.encryption_key:
            return json.dumps(payload).encode()
            
        fernet = Fernet(TransportManager.config.encryption_key)
        return fernet.encrypt(json.dumps(payload).encode())

    def _sign_message(self, signer: MessageSigner) -> str:
        """Generate HMAC signature for message integrity"""
        payload_hash = hashlib.sha256(self.payload).hexdigest()
        return signer.generate_signature(f"{self.id}{self.sender}{self.recipient}{payload_hash}")

    def validate(self, signer: MessageSigner) -> bool:
        """Verify message integrity and protocol version"""
        if self.protocol != "mesh.v2":
            raise ValueError("Unsupported protocol version")
            
        if not signer.verify_signature(self.signature):
            raise SecurityError("Invalid message signature")
            
        return True

    def to_network_format(self) -> bytes:
        """Serialize for transmission with size check"""
        data = json.dumps({
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "timestamp": self.timestamp,
            "protocol": self.protocol,
            "payload": self.payload.decode(),
            "signature": self.signature
        }).encode()
        
        if len(data) > TransportManager.config.max_payload_size:
            raise PayloadTooLargeError()
            
        return data

class TransportManager:
    config = TransportConfig()
    _circuit_state = {}
    _lock = threading.Lock()
    
    def __init__(self):
        self._queue = []
        self._active = True
        self._worker = threading.Thread(target=self._process_queue)
        self._worker.start()

    @circuit(failure_threshold=5, recovery_timeout=60)
    def send(self, packet: MessagePacket) -> bool:
        """Reliable message delivery with exponential backoff"""
        start_time = time.time()
        
        for attempt in range(self.config.max_retries + 1):
            try:
                result = self._attempt_send(packet)
                TRANSPORT_SUCCESS.labels(packet.protocol).inc()
                return True
            except (NetworkError, SecurityError) as e:
                TRANSPORT_FAILURE.labels(packet.protocol, e.__class__.__name__).inc()
                
                if attempt == self.config.max_retries:
                    self._dead_letter_queue(packet, e)
                    return False
                    
                sleep_time = self.config.base_timeout * (self.config.backoff_factor ** attempt)
                time.sleep(sleep_time)
                
        TRANSPORT_LATENCY.labels(packet.protocol).observe(time.time() - start_time)
        return False

    def _attempt_send(self, packet: MessagePacket):
        """Actual transport implementation with validation"""
        # Validate before sending
        if len(packet.to_network_format()) > self.config.max_payload_size:
            raise PayloadTooLargeError()
            
        # Protocol-specific transport logic
        if packet.protocol == "mesh.v2":
            return self._send_mesh_v2(packet)
            
        raise UnsupportedProtocolError()

    def _send_mesh_v2(self, packet: MessagePacket):
        """Production-grade mesh transport implementation"""
        # Implement actual network I/O here
        # Placeholder for demonstration
        logging.info(f"Routing {packet.id} via mesh.v2")
        return True

    def async_send(self, packet: MessagePacket):
        """Non-blocking queue-based delivery"""
        with self._lock:
            self._queue.append(packet)
            TRANSPORT_QUEUE.set(len(self._queue))

    def _process_queue(self):
        """Background queue processing"""
        while self._active:
            with self._lock:
                if self._queue:
                    packet = self._queue.pop(0)
                    TRANSPORT_QUEUE.set(len(self._queue))
                    self.send(packet)
                    
            time.sleep(0.1)

    def _dead_letter_queue(self, packet: MessagePacket, error: Exception):
        """Handle undeliverable messages"""
        logging.error(f"Message {packet.id} failed permanently: {error}")
        # Implement DLQ integration (e.g., Kafka topic, S3 bucket)

    def shutdown(self):
        """Graceful termination"""
        self._active = False
        self._worker.join()

# Example usage:
config = TransportConfig(
    encryption_key=Fernet.generate_key().decode(),
    max_retries=5,
    base_timeout=2.0
)
TransportManager.config = config

signer = MessageSigner("secret-api-key")
packet = MessagePacket(
    sender="comms-node-1",
    recipient="ai-core-5",
    payload={"command": "refresh_model"},
    signer=signer
)

transport = TransportManager()
transport.async_send(packet)

# Load from environment variables
TransportManager.config = TransportConfig(
    encryption_key=os.getenv('TRANSPORT_KEY'),
    max_retries=int(os.getenv('MAX_RETRIES', 3)),
    base_timeout=float(os.getenv('BASE_TIMEOUT', 1.0))
)

# Sample Prometheus queries
'rate(transport_failure_total[5m]) by (error_type)'
'histogram_quantile(0.95, sum(rate(transport_latency_seconds_bucket[5m])) by (le)' 

try:
    transport.send(packet)
except CircuitBreakerError:
    # Alert on systemic failures
    alert_system("Transport circuit open!")
except PayloadTooLargeError:
    # Handle oversized messages
    compress_payload(packet)