import os
from typing import Dict, Any, Type, Optional
from .base import BaseDriver
from .communication.gmail import GmailDriver
from .task_creation.linear import LinearDriver
from ...models import OrchestrationStatus

class MockDriver(BaseDriver):
    """
    Standard fallback driver used for demonstrations or when real integration keys are missing.
    """

    def check_health(self) -> bool:
        """
        Always returns True for the mock driver.
        Returns:
            bool: Always True.
        """
        return True

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate execution for the mock driver.
        Args:
            payload (Dict[str, Any]): The payload to simulate.
        Returns:
            Dict[str, Any]: Simulated result.
        """
        return {
            "status": "SUCCESS",
            "is_recoverable": False,
            "result": {"provider": "Mock_System", "mode": "simulation", "payload_received": payload}
        }

class DriverRegistry:
    """
    Registry to manage and route StepTypes to concrete Driver implementations.
    Supports ENABLED toggles via environment variables.
    """
    _drivers: Dict[str, type]
    _mock_driver: BaseDriver

    def __init__(self) -> None:
        """
        Initialize the driver registry.
        """
        self._drivers = {}
        self._mock_driver = MockDriver()

    def register(self, step_type: str, driver_class: type) -> None:
        """
        Register a driver class for a given step type.
        Args:
            step_type (str): The step type.
            driver_class (type): The driver class to register.
        """
        self._drivers[step_type] = driver_class

    def get_driver(self, step_type: str, force_live: bool = False) -> BaseDriver:
        """
        Retrieves a driver for the given StepType.
        If force_live is True, it will raise an error if the real driver is disabled.

        Args:
            step_type (str): The step type.
            force_live (bool): Require live driver.

        Returns:
            BaseDriver: The driver instance.
        """
        driver_class = self._drivers.get(step_type)
        if driver_class:
            # check the ENV toggle, e.g., OPSAI_DRIVER_GMAIL_ENABLED
            env_key: str = f"OPSAI_DRIVER_{step_type}_ENABLED"
            if os.getenv(env_key, "false").lower() == "true":
                return driver_class()
            if force_live:
                import logging
                logger = logging.getLogger("opsai")
                logger.critical(f"CRITICAL: Driver for {step_type} ({driver_class.__name__}) is REQUIRED to be LIVE but is currently DISABLED in configuration.")
                raise RuntimeError(f"CRITICAL: Driver for {step_type} ({driver_class.__name__}) is REQUIRED to be LIVE but is currently DISABLED in configuration.")
        # Fallback to mock
        return self._mock_driver

# Global instance
registry = DriverRegistry()
registry.register("COMMUNICATION", GmailDriver)
registry.register("TASK_CREATION", LinearDriver)

def driver_startup_check() -> None:
    """
    Utility to verify all enabled drivers are healthy on startup.
    Called by main.py.
    """
    import logging
    logger = logging.getLogger("opsai")
    logger.info("🛡️  OpsAI Driver Startup Check:")
    
    # 1. Base Mock (Default)
    logger.info("   - [MockDriver]: HEALTHY (Simulation Mode)")

    # 2. Iterate through StepTypes and their registered drivers
    # Note: We use a set to avoid checking the same class twice if registered to multiple types
    checked_drivers = set()
    
    for step_type, driver_class in registry._drivers.items():
        if driver_class in checked_drivers:
            continue
        env_key: str = f"OPSAI_DRIVER_{step_type}_ENABLED"
        is_enabled: bool = os.getenv(env_key, "false").lower() == "true"
        if is_enabled:
            instance: BaseDriver = driver_class()
            is_healthy: bool = instance.check_health()
            status_icon: str = "✅" if is_healthy else "❌"
            status_text: str = "HEALTHY" if is_healthy else "CONFIGURATION ERROR"
            logger.info(f"   {status_icon} [{driver_class.__name__}]: {status_text}")
        else:
            logger.info(f"   ⚪ [{driver_class.__name__}]: DISABLED (Mock Fallback Active)")
        checked_drivers.add(driver_class)
    logger.info("")
