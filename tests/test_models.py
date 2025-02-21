import pytest
from models import Task, Project  # Update these imports based on your actual models

def test_task_creation():
    task = Task(
        description="Test task",
        project="Test Project",
        tags=["test", "important"]
    )
    assert task.description == "Test task"
    assert task.project == "Test Project"
    assert "test" in task.tags
    assert "important" in task.tags

def test_task_completion():
    task = Task(description="Test task")
    assert not task.completed
    task.complete()
    assert task.completed

def test_project_tasks():
    project = Project("Test Project")
    task1 = Task(description="Task 1", project="Test Project")
    task2 = Task(description="Task 2", project="Test Project")
    
    project.add_task(task1)
    project.add_task(task2)
    
    assert len(project.tasks) == 2
    assert task1 in project.tasks

def test_model_creation():
    # Add tests for model initialization
    pass

def test_model_methods():
    # Add tests for model methods
    pass 