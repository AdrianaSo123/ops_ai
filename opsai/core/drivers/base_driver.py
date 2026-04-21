from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import logging

class BaseDriver(ABC):
    """
    Abstract Base Class for all Integration Drivers.
    Each driver is responsible for taking a 'Planned Action' payload 
    and delivering it to a third-party service.
    """
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Driver-{name}")
        self.api_key = self._get_required_env()

    @abstractmethod
    def _get_required_env(self) -> Optional[str]:
        """Returns the ENV variable name required for this driver."""
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the integration call. 
        If API key is missing, triggers 'Dry Run' simulation.
        """
        pass

    def log_dry_run(self, payload: Dict[str, Any]):
        """Logs the structured payload for an integration audit."""
        self.logger.warning(f"--- [DRY RUN] {self.name} ---")
        self.logger.warning(f"Simulating API call with payload: {payload}")
        return {
            "status": "dry_run",
            "driver": self.name,
            "simulated_payload": payload,
            "instructions": f"Add {self._get_required_env()} to .env to go live."
        }
