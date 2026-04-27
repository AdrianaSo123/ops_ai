"""
retry_handler.py — Retry Handler for OpsAI Phase 4
Implements retry logic and exponential backoff strategy.
Follows SOLID principles and is fully type-annotated and documented.
"""
from typing import Dict, Any
import time

class RetryHandler:
    """
    Handles retry logic for workflow steps, including delay strategies.
    """
    def get_delay(self, retry_policy: Dict[str, Any], retry_count: int) -> float:
        """
        Calculate delay before next retry based on strategy.
        Args:
            retry_policy (dict): Retry policy with strategy and base_delay_seconds.
            retry_count (int): Current retry attempt.
        Returns:
            float: Delay in seconds.
        """
        strategy = retry_policy.get("strategy", "exponential_backoff")
        base = retry_policy.get("base_delay_seconds", 1)
        if strategy == "exponential_backoff":
            return base * (2 ** retry_count)
        return base

    def delay(self, retry_policy: Dict[str, Any], retry_count: int) -> None:
        """
        Sleep for the calculated delay (for real execution, not used in tests).
        """
        delay: float = self.get_delay(retry_policy, retry_count)
        time.sleep(delay)
