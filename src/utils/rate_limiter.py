"""
Rate limiter utility for session-based query limits.
"""

import time
import streamlit as st

class RateLimiter:
    """Session-agnostic rate limiter for user queries."""

    def __init__(self, limit: int = 20, window_minutes: int = 60):
        self.limit = limit
        self.window_seconds = window_minutes * 60

    def get_status(self, data_store: dict) -> tuple:
        """
        Returns (remaining, reset_in_mins)
        
        Args:
            data_store: A reference to a dictionary where rate limit data is stored.
                        (e.g., st.session_state or a specific user's entry in a global dict)
        """
        if "rate_limit_data" not in data_store:
            data_store["rate_limit_data"] = {
                "count": 0,
                "start_time": time.time()
            }

        now = time.time()
        elapsed = now - data_store["rate_limit_data"]["start_time"]

        # Reset window if time expired
        if elapsed > self.window_seconds:
            data_store["rate_limit_data"] = {
                "count": 0,
                "start_time": now
            }
            elapsed = 0

        remaining = max(0, self.limit - data_store["rate_limit_data"]["count"])
        reset_in = max(0, int((self.window_seconds - elapsed) / 60))
        return remaining, reset_in

    def increment(self, data_store: dict):
        """Increment the query count."""
        if "rate_limit_data" in data_store:
            data_store["rate_limit_data"]["count"] += 1

    def is_limited(self, data_store: dict) -> bool:
        """Check if user has reached the limit."""
        remaining, _ = self.get_status(data_store)
        return remaining <= 0
