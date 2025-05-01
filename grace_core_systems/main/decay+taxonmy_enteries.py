// Example entropy_log.json
{
  "timestamp": "2023-10-05T14:23:18Z",
  "anchor_id": "anchor_789",
  "decay_reason": "contradiction",
  "conflicting_anchors": ["anchor_123", "anchor_456"],
  "resolution": {
    "action": "deprecated",
    "confidence_loss": 0.4,
    "new_rules": [
      "Avoid references to deprecated API v1.2",
      "Increase context weight for security-related anchors"
    ]
  }
}