import pytest
from ui_components import TaskList, FilterManager  # Update based on your actual classes

def test_task_filtering():
    filter_manager = FilterManager()
    
    # Test project filtering
    filter_manager.set_project_filter("Work")
    assert filter_manager.current_project == "Work"
    
    # Test tag filtering
    filter_manager.set_tag_filter("urgent")
    assert "urgent" in filter_manager.active_tags

def test_task_list_sorting():
    task_list = TaskList()
    
    # Add some test tasks
    task_list.add_task({"description": "Low priority", "priority": "L"})
    task_list.add_task({"description": "High priority", "priority": "H"})
    
    sorted_tasks = task_list.get_sorted_tasks("priority")
    assert sorted_tasks[0]["priority"] == "H"

def test_ui_component_creation():
    # Add tests for UI component initialization
    pass

def test_ui_component_properties():
    # Add tests for component properties
    pass 