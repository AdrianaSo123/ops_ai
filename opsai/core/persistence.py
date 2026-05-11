"""
persistence.py — Persistence Layer for OpsAI Phase 4
Implements repository/service pattern for saving and loading workflow state.
Follows SOLID principles and is fully type-annotated and documented.
"""
from typing import Any, Dict, Optional
import json
import os
from pathlib import Path

class PersistenceRepository:
    """
    Handles low-level persistence operations for workflow state.
    Supports JSON file storage (MVP).
    """
    base_dir: Path

    def __init__(self, base_dir: str = "data/orchestrations") -> None:
        """
        Initialize the repository.
        Args:
            base_dir (str): Directory for storing orchestration state files.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, workflow_id: str, state: Dict[str, Any]) -> None:
        """
        Save workflow state to a JSON file.
        Args:
            workflow_id (str): The workflow identifier.
            state (Dict[str, Any]): The state to persist.
        """
        file_path = self.base_dir / f"{workflow_id}.json"
        with open(file_path, "w") as f:
            json.dump(state, f, indent=2)

    def load(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow state from a JSON file. Returns None if not found or corrupted.
        Args:
            workflow_id (str): The workflow identifier.
        Returns:
            Optional[Dict[str, Any]]: The loaded state or None.
        """
        file_path = self.base_dir / f"{workflow_id}.json"
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception:
            return None

class PersistenceService:
    """
    High-level persistence service for orchestrator and CLI.
    Decouples business logic from storage details.
    """
    repository: PersistenceRepository

    def __init__(self, repository: PersistenceRepository) -> None:
        """
        Initialize the service.
        Args:
            repository (PersistenceRepository): The repository instance.
        """
        self.repository = repository

    def save_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        """
        Save workflow state.
        Args:
            workflow_id (str): The workflow identifier.
            state (Dict[str, Any]): The state to persist.
        """
        self.repository.save(workflow_id, state)

    def load_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow state.
        Args:
            workflow_id (str): The workflow identifier.
        Returns:
            Optional[Dict[str, Any]]: The loaded state or None.
        """
        return self.repository.load(workflow_id)
