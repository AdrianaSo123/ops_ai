import os
from typing import Dict, Any, Type, Optional
from .base import BaseDriver
from .communication.gmail import GmailDriver
from .task_creation.linear import LinearDriver
from ...models import OrchestrationStatus

class MockDriver(BaseDriver):
    """
    Standard fallback driver used for demonstrations or when 
    real integration keys are missing.
    """
    def check_health(self) -> bool:
        return True # Mocks are always healthy

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
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
    def __init__(self):
        self._drivers: Dict[str, Type[BaseDriver]] = {}
        # Default mock fallback
        self._mock_driver = MockDriver()

    def register(self, step_type: str, driver_class: Type[BaseDriver]):
        self._drivers[step_type] = driver_class

    def get_driver(self, step_type: str, force_live: bool = False) -> BaseDriver:
        """
        Retrieves a driver for the given StepType.
        If force_live is True, it will raise an error if the real driver is disabled.
        """
        driver_class = self._drivers.get(step_type)
        
        if driver_class:
            # check the ENV toggle, e.g., OPSAI_DRIVER_GMAIL_ENABLED
            env_key = f"OPSAI_DRIVER_{step_type}_ENABLED"
            if os.getenv(env_key, "false").lower() == "true":
                return driver_class()
            
            if force_live:
                raise ValueError(f"CRITICAL: Driver for {step_type} ({driver_class.__name__}) is REQUIRED to be LIVE but is currently DISABLED in configuration.")
        
        # 2. Fallback to mock
        return self._mock_driver

# Global instance
registry = DriverRegistry()
registry.register("COMMUNICATION", GmailDriver)
registry.register("TASK_CREATION", LinearDriver)

def driver_startup_check():
    """
    Utility to verify all enabled drivers are healthy on startup.
    Called by main.py.
    """
    print("\n🛡️  OpsAI Driver Startup Check:")
    
    # 1. Base Mock (Default)
    print("   - [MockDriver]: HEALTHY (Simulation Mode)")

    # 2. Iterate through StepTypes and their registered drivers
    # Note: We use a set to avoid checking the same class twice if registered to multiple types
    checked_drivers = set()
    
    for step_type, driver_class in registry._drivers.items():
        if driver_class in checked_drivers:
            continue
            
        env_key = f"OPSAI_DRIVER_{step_type}_ENABLED"
        is_enabled = os.getenv(env_key, "false").lower() == "true"
        
        if is_enabled:
            instance = driver_class()
            is_healthy = instance.check_health()
            status_icon = "✅" if is_healthy else "❌"
            status_text = "HEALTHY" if is_healthy else "CONFIGURATION ERROR"
            print(f"   {status_icon} [{driver_class.__name__}]: {status_text}")
        else:
            print(f"   ⚪ [{driver_class.__name__}]: DISABLED (Mock Fallback Active)")
            
        checked_drivers.add(driver_class)
    print("")
