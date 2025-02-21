from typing import List, Dict, Optional
from datetime import datetime

class TaskService:
    """Handles business logic for task operations"""
    
    def __init__(self):
        self.tasks = []
    
    def add_task(self, description: str, project: Optional[str] = None, 
                 tags: Optional[List[str]] = None, due: Optional[str] = None) -> Dict:
        """Creates a new task with validation"""
        if not description.strip():
            raise ValueError("Task description cannot be empty")
            
        task = {
            "description": description,
            "project": project,
            "tags": tags or [],
            "created": datetime.now(),
            "completed": False
        }
        
        if due:
            try:
                datetime.strptime(due, "%Y-%m-%d")
                task["due"] = due
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
                
        self.tasks.append(task)
        return task
    
    def get_tasks_by_project(self, project: str) -> List[Dict]:
        """Filter tasks by project"""
        return [task for task in self.tasks if task.get("project") == project]
    
    def get_tasks_by_tags(self, tags: List[str]) -> List[Dict]:
        """Filter tasks by tags"""
        return [
            task for task in self.tasks 
            if any(tag in task.get("tags", []) for tag in tags)
        ]
    
    def sort_tasks(self, tasks: List[Dict], sort_by: str = "created") -> List[Dict]:
        """Sort tasks by given criteria"""
        if sort_by == "priority":
            priority_order = {"H": 0, "M": 1, "L": 2}
            return sorted(tasks, key=lambda x: priority_order.get(x.get("priority", "L")))
        elif sort_by == "due":
            return sorted(tasks, key=lambda x: x.get("due") or "9999-12-31")
        return sorted(tasks, key=lambda x: x.get(sort_by)) 