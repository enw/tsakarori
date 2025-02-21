import pytest
from datetime import datetime
from task_service import TaskService

@pytest.fixture
def task_service():
    return TaskService()

def test_add_task(task_service):
    # Test basic task creation
    task = task_service.add_task("Test task")
    assert task["description"] == "Test task"
    assert not task["completed"]
    assert isinstance(task["created"], datetime)
    
    # Test task with all fields
    full_task = task_service.add_task(
        description="Full task",
        project="Test Project",
        tags=["important", "urgent"],
        due="2024-03-20"
    )
    assert full_task["project"] == "Test Project"
    assert "important" in full_task["tags"]
    assert full_task["due"] == "2024-03-20"

def test_add_task_validation(task_service):
    # Test empty description
    with pytest.raises(ValueError):
        task_service.add_task("")
        
    # Test invalid date
    with pytest.raises(ValueError):
        task_service.add_task("Task with bad date", due="invalid-date")

def test_task_filtering(task_service):
    # Add some test tasks
    task_service.add_task("Work task 1", project="Work", tags=["urgent"])
    task_service.add_task("Work task 2", project="Work", tags=["normal"])
    task_service.add_task("Home task", project="Home", tags=["urgent"])
    
    # Test project filtering
    work_tasks = task_service.get_tasks_by_project("Work")
    assert len(work_tasks) == 2
    assert all(t["project"] == "Work" for t in work_tasks)
    
    # Test tag filtering
    urgent_tasks = task_service.get_tasks_by_tags(["urgent"])
    assert len(urgent_tasks) == 2
    assert all("urgent" in t["tags"] for t in urgent_tasks)

def test_task_sorting(task_service):
    # Add tasks with different priorities
    task_service.add_task("Low priority", priority="L")
    task_service.add_task("High priority", priority="H")
    task_service.add_task("Medium priority", priority="M")
    
    # Test priority sorting
    sorted_tasks = task_service.sort_tasks(task_service.tasks, "priority")
    assert sorted_tasks[0]["priority"] == "H"
    assert sorted_tasks[-1]["priority"] == "L" 