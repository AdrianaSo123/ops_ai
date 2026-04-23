import pytest
from opsai.core.persistence import PersistenceRepository, PersistenceService
import tempfile
import shutil
import os

def test_save_and_load_state():
    temp_dir = tempfile.mkdtemp()
    try:
        repo = PersistenceRepository(base_dir=temp_dir)
        service = PersistenceService(repo)
        workflow_id = "test123"
        state = {"workflow_id": workflow_id, "steps": [1, 2, 3], "status": "running"}
        service.save_state(workflow_id, state)
        loaded = service.load_state(workflow_id)
        assert loaded == state
    finally:
        shutil.rmtree(temp_dir)

def test_load_missing_state():
    temp_dir = tempfile.mkdtemp()
    try:
        repo = PersistenceRepository(base_dir=temp_dir)
        service = PersistenceService(repo)
        assert service.load_state("doesnotexist") is None
    finally:
        shutil.rmtree(temp_dir)

def test_load_corrupted_state():
    temp_dir = tempfile.mkdtemp()
    try:
        repo = PersistenceRepository(base_dir=temp_dir)
        service = PersistenceService(repo)
        workflow_id = "corrupt"
        file_path = os.path.join(temp_dir, f"{workflow_id}.json")
        with open(file_path, "w") as f:
            f.write("not a json")
        assert service.load_state(workflow_id) is None
    finally:
        shutil.rmtree(temp_dir)
