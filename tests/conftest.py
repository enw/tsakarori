import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

@pytest.fixture
def sample_task():
    """Fixture to create a sample task for testing"""
    return {
        "description": "Test task",
        "project": "Test Project",
        "tags": ["test"],
        "priority": "M",
        "due": "2024-03-20"
    }

@pytest.fixture
def sample_project():
    """Fixture to create a sample project with tasks"""
    return {
        "name": "Test Project",
        "tasks": [
            {"description": "Task 1", "priority": "H"},
            {"description": "Task 2", "priority": "M"}
        ]
    } 