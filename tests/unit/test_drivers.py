import pytest
import os
from opsai.core.drivers.registry import DriverRegistry, MockDriver
from opsai.core.drivers.communication.gmail import GmailDriver
from opsai.core.drivers.base import BaseDriver

def test_registry_registration():
    """Verify that drivers can be registered and retrieved."""
    registry = DriverRegistry()
    registry.register("TEST_TYPE", MockDriver)
    
    driver = registry.get_driver("TEST_TYPE")
    assert isinstance(driver, MockDriver)

def test_registry_fallback(monkeypatch):
    """Verify that registry falls back to mock if real driver is disabled."""
    registry = DriverRegistry()
    registry.register("COMMUNICATION", GmailDriver)
    
    # Force the toggle to false
    monkeypatch.setenv("OPSAI_DRIVER_COMMUNICATION_ENABLED", "false")
    
    driver = registry.get_driver("COMMUNICATION")
    # Should fall back to mock
    assert isinstance(driver, MockDriver)

def test_mock_driver_execution():
    """Verify the MockDriver returns a success status."""
    driver = MockDriver()
    import asyncio
    
    # Run async execution in a sync test
    result = asyncio.run(driver.execute({"test": "data"}))
    assert result["status"] == "SUCCESS"
    assert "Mock_System" in result["result"]["provider"]

def test_gmail_driver_health_logic(monkeypatch):
    """Verify GmailDriver health check logic handles missing keys."""
    monkeypatch.setenv("OPSAI_DRIVER_GMAIL_USER", "")
    monkeypatch.setenv("OPSAI_DRIVER_GMAIL_PASS", "")
    
    driver = GmailDriver()
    assert driver.check_health() is False
