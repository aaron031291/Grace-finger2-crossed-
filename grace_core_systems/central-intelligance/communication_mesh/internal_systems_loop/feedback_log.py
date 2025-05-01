# internal_system_loop/feedback_log.py

import os
import json
import logging
import threading
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass

import structlog
from prometheus_client import Counter, Histogram, Gauge

# --- Structured Logging Setup ---
structlog.configure(
    processors=[structlog.processors.JSONRenderer(sort_keys=True)],
    logger_factory=structlog.PrintLoggerFactory()
)

# --- Prometheus Metrics ---
FEEDBACK_ACTIONS = Counter(
    'feedback_actions_total',
    'Total feedback events by action type',
    ['source', 'action']
)

CONFIDENCE_HISTOGRAM = Histogram(
    'feedback_confidence',
    'Confidence score distribution',
    ['source'],
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
)

LOG_LATENCY = Histogram(
    'feedback_log_latency_seconds',
    'Feedback logging processing time (seconds)'
)

ACTIVE_FEEDBACK = Gauge(
    'feedback_active_entries',
    'Currently buffered feedback entries'
)

# --- Feedback Entry Dataclass ---
@dataclass
class FeedbackEntry:
    anchor_id: str
    action: str
    source: str  # e.g. trigger_router, learning_loop, entropy_filter
    confidence: float
    metadata: Dict
    timestamp: str

# --- Feedback Logger Class ---
class FeedbackLogger:
    def __init__(self, prometheus_enabled: bool = True, siem_endpoint: Optional[str] = None):
        self._buffer = []
        self._lock = threading.Lock()
        self.prometheus_enabled = prometheus_enabled
        self.siem_endpoint = siem_endpoint
        self.logger = structlog.get_logger()

    @LOG_LATENCY.time()
    def log_feedback(self, anchor_id: str, action: str, source: str, confidence: float, metadata: Optional[Dict] = None) -> None:
        """Core logging method with thread-safe buffering"""
        entry = FeedbackEntry(
            anchor_id=anchor_id,
            action=action,
            source=source,
            confidence=confidence,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat()
        )

        with self._lock:
            self._buffer.append(entry)
            ACTIVE_FEEDBACK.set(len(self._buffer))

            if action in ('ethical_violation', 'system_failure'):
                self._flush_buffer()

    def _flush_buffer(self):
        with self._lock:
            for entry in self._buffer:
                self._structured_log(entry)
                self._update_metrics(entry)
                self._send_to_siem(entry)
            self._buffer.clear()
            ACTIVE_FEEDBACK.set(0)

    def _structured_log(self, entry: FeedbackEntry):
        self.logger.info("feedback", **{
            "anchor": entry.anchor_id,
            "action": entry.action,
            "source": entry.source,
            "confidence": round(entry.confidence, 2),
            "meta": entry.metadata,
            "timestamp": entry.timestamp
        })

    def _update_metrics(self, entry: FeedbackEntry):
        if self.prometheus_enabled:
            FEEDBACK_ACTIONS.labels(source=entry.source, action=entry.action).inc()
            CONFIDENCE_HISTOGRAM.labels(source=entry.source).observe(entry.confidence)

    def _send_to_siem(self, entry: FeedbackEntry):
        if not self.siem_endpoint:
            return
        try:
            # Placeholder for actual HTTP post to SIEM
            pass
        except Exception as e:
            logging.error(f"SIEM delivery failed: {str(e)}")

    def periodic_flush(self):
        """Called by loop controller or scheduler"""
        self._flush_buffer()

# --- Singleton Instance ---
feedback_logger = FeedbackLogger(
    prometheus_enabled=True,
    siem_endpoint=os.getenv('SIEM_ENDPOINT')
)

"""
Enterprise Feedback Loop Architecture

    Feedback Sources
        ├── Structured Logging  → Audit Trail
        ├── Prometheus Metrics  → Observability
        └── SIEM Integration    → Security Monitoring

Mermaid-style Topology (external rendering):

    graph TD
        A[Feedback Sources] --> B[Structured Logging]
        A --> C[Prometheus Metrics]
        A --> D[SIEM Integration]
        B --> E[Audit Trail]
        C --> F[Observability]
        D --> G[Security Monitoring]

        style A fill:#fab1a0,stroke:#e17055
        style B fill:#ffeaa7,stroke:#fdcb6e
        style C fill:#81ecec,stroke:#00cec9
        style D fill:#dfe6e9,stroke:#636e72
        style E fill:#55efc4,stroke:#00b894
        style F fill:#74b9ff,stroke:#0984e3
        style G fill:#fd79a8,stroke:#e84393
"""