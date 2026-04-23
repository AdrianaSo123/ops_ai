import pytest
from opsai.core.retry_handler import RetryHandler

def test_exponential_backoff():
    handler = RetryHandler()
    policy = {"strategy": "exponential_backoff", "base_delay_seconds": 2}
    assert handler.get_delay(policy, 0) == 2
    assert handler.get_delay(policy, 1) == 4
    assert handler.get_delay(policy, 2) == 8

def test_default_strategy():
    handler = RetryHandler()
    policy = {"base_delay_seconds": 3}
    assert handler.get_delay(policy, 0) == 3
    assert handler.get_delay(policy, 1) == 6
