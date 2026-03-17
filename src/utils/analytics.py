import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)

class AnalyticsManager:
    """
    Manages chat event logging to GCS for usage analytics.
    Events are stored as individual JSON files in the 'analytics/' prefix.
    """

    def __init__(self, bucket_name: Optional[str] = None):
        self.bucket_name = bucket_name or os.getenv("GCS_BUCKET_NAME", "")
        self.prefix = "analytics"
        self._client = None
        self._bucket = None

    @property
    def enabled(self) -> bool:
        return bool(self.bucket_name)

    def _get_bucket(self):
        if self._bucket:
            return self._bucket
        if not self.enabled:
            return None
        
        try:
            from google.cloud import storage
            self._client = storage.Client()
            self._bucket = self._client.bucket(self.bucket_name)
            return self._bucket
        except Exception as e:
            logger.warning(f"Analytics: Failed to connect to GCS: {e}")
            self.bucket_name = "" # Disable for this session
            return None

    def log_chat_event(self, event_data: Dict[str, Any]):
        """
        Log a chat event to GCS. 
        schema: timestamp, user_email, query, response_time, tokens, sources, is_error
        """
        if not self.enabled:
            # Fallback to local file if GCS is disabled
            self._log_locally(event_data)
            return

        try:
            bucket = self._get_bucket()
            if not bucket:
                self._log_locally(event_data)
                return

            timestamp = datetime.now().isoformat().replace(":", "-")
            event_id = str(uuid.uuid4())[:8]
            blob_name = f"{self.prefix}/chat_{timestamp}_{event_id}.json"
            
            blob = bucket.blob(blob_name)
            blob.upload_from_string(
                data=json.dumps(event_data, indent=2),
                content_type="application/json"
            )
            logger.info(f"📊 Analytics: Logged chat event to gs://{self.bucket_name}/{blob_name}")
        except Exception as e:
            logger.error(f"Analytics: Failed to log event to GCS: {e}")
            self._log_locally(event_data)

    def _log_locally(self, event_data: Dict[str, Any]):
        """Fallback to local JSONL file."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "usage_analytics.jsonl"
        
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event_data) + "\n")
            logger.info("📊 Analytics: Logged chat event locally (fallback)")
        except Exception as e:
            logger.error(f"Analytics: Failed to log event locally: {e}")

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Fetch all logged events from GCS and local fallback."""
        events = []
        
        # 1. Load from local fallback
        log_file = Path("logs/usage_analytics.jsonl")
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            events.append(json.loads(line))
            except Exception as e:
                logger.error(f"Analytics: Failed to read local logs: {e}")

        # 2. Load from GCS
        if self.enabled:
            try:
                bucket = self._get_bucket()
                if bucket:
                    blobs = bucket.list_blobs(prefix=self.prefix)
                    for blob in blobs:
                        if blob.name.endswith(".json"):
                            content = blob.download_as_text()
                            events.append(json.loads(content))
            except Exception as e:
                logger.error(f"Analytics: Failed to fetch logs from GCS: {e}")

        return events

# Singleton instance
analytics_manager = AnalyticsManager()
