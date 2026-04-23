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
    def __init__(self, base_dir: str = "data/orchestrations"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, workflow_id: str, state: Dict[str, Any]) -> None:
        """Save workflow state to a JSON file."""
        file_path = self.base_dir / f"{workflow_id}.json"
        with open(file_path, "w") as f:
            json.dump(state, f, indent=2)

    def load(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from a JSON file. Returns None if not found or corrupted."""
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
    def __init__(self, repository: PersistenceRepository):
        self.repository = repository

    def save_state(self, workflow_id: str, state: Dict[str, Any]) -> None:
        self.repository.save(workflow_id, state)

    def load_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self.repository.load(workflow_id)
