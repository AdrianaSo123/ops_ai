from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseDriver(ABC):
    """
    Abstract Base Class for all OpsAI Integration Drivers.
    Drivers are responsible for translating generalized AI payloads 
    into provider-specific API calls.
    """
    
    @abstractmethod
    def check_health(self) -> bool:
        """
        Validates credentials and connectivity on startup.
        Should return True if correctly configured, otherwise False.
        """
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the action.
        
        Returns: 
            Dict containing: 
            - 'status': 'SUCCESS' | 'FAILED'
            - 'is_recoverable': bool (True for transient network/5xx errors)
            - 'result': dict (Raw sanitized API result)
            - 'error': str (Optional error message)
        """
        pass

    def sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optional hook to mask PII or Secrets before 
        persisting driver results to the StepStatus table.
        """
        # Default implementation: Return as-is
        return data
