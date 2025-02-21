from tasklib import TaskWarrior, Task
from datetime import datetime


class TaskManager:
    def __init__(self):
        self.tw = TaskWarrior()
        self.current_tasks = []
        self.projects = []
        self.tags = []
        self.filter_project = None
        self.filter_tag = None
        self.filter_text = None
        self.show_completed = False
        self.update_task_lists()

    def update_task_lists(self):
        """Update task lists with current filters"""
        # Get tasks based on completion status
        if self.show_completed:
            tasks = list(self.tw.tasks.pending()) + list(self.tw.tasks.completed())
        else:
            tasks = self.tw.tasks.pending()

        # Apply filters in sequence
        if self.filter_project:
            tasks = [t for t in tasks if t["project"] == self.filter_project]

        if self.filter_tag:
            tasks = [t for t in tasks if self.filter_tag in (t["tags"] or [])]

        if self.filter_text and self.filter_text.strip():
            filtered = []
            search_text = self.filter_text.lower().strip()

            for task in tasks:
                # Check description
                description = task["description"].lower() if task["description"] else ""
                if search_text in description:
                    filtered.append(task)
                    continue

                # Check project
                project = task["project"].lower() if task["project"] else ""
                if search_text in project:
                    filtered.append(task)
                    continue

                # Check tags
                tags = [t.lower() for t in (task["tags"] or [])]
                if any(search_text in tag for tag in tags):
                    filtered.append(task)
                    continue

            tasks = filtered

        # Update the task lists
        self.current_tasks = list(tasks)
        self.current_tasks.sort(
            key=lambda x: (x["status"] == "completed", -float(x["urgency"] or 0.0))
        )

        # Update available projects and tags based on filtered tasks
        self.projects = sorted(
            set(task["project"] for task in self.current_tasks if task["project"])
        )
        self.tags = sorted(
            set(tag for task in self.current_tasks for tag in (task["tags"] or []))
        )

    def add_task(self, description, project=None, tags=None):
        task = Task(self.tw)
        task["description"] = description
        if project:
            task["project"] = project
        if tags:
            task["tags"] = tags
        task.save()
        self.update_task_lists()

    def edit_task(
        self,
        task_idx,
        description=None,
        project=None,
        tags=None,
        priority=None,
        due_date=None,
    ):
        if not self.current_tasks or task_idx >= len(self.current_tasks):
            return

        task = self.current_tasks[task_idx]
        if description:
            task["description"] = description
        if project:
            task["project"] = project
        if tags is not None:
            task["tags"] = tags
        if priority and priority.upper() in ["H", "M", "L"]:
            task["priority"] = priority.upper()
        if due_date:
            try:
                task["due"] = datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                pass

        task.save()
        self.update_task_lists()

    def delete_task(self, task_idx):
        if task_idx < len(self.current_tasks):
            self.current_tasks[task_idx].delete()
            self.update_task_lists()

    def complete_task(self, task_idx):
        if task_idx < len(self.current_tasks):
            self.current_tasks[task_idx].done()
            self.update_task_lists()

    def get_tasks_by_project(self):
        """Return tasks organized by project"""
        by_project = {}
        no_project_tasks = []

        for task in self.current_tasks:
            project = task["project"]
            if project:
                if project not in by_project:
                    by_project[project] = []
                by_project[project].append(task)
            else:
                no_project_tasks.append(task)

        # Sort projects alphabetically
        sorted_projects = sorted(by_project.keys())

        # Sort tasks within each project by urgency
        for project in by_project:
            by_project[project].sort(
                key=lambda x: float(x["urgency"] or 0.0), reverse=True
            )

        # Sort no-project tasks by urgency
        no_project_tasks.sort(key=lambda x: float(x["urgency"] or 0.0), reverse=True)

        return sorted_projects, by_project, no_project_tasks

    def get_tasks_by_tag(self):
        """Return tasks organized by tag"""
        by_tag = {}
        no_tag_tasks = []

        for task in self.current_tasks:
            tags = task["tags"] or []
            if tags:
                for tag in tags:
                    if tag not in by_tag:
                        by_tag[tag] = []
                    by_tag[tag].append(task)
            else:
                no_tag_tasks.append(task)

        # Sort tags alphabetically
        sorted_tags = sorted(by_tag.keys())

        # Sort tasks within each tag by urgency
        for tag in by_tag:
            by_tag[tag].sort(key=lambda x: float(x["urgency"] or 0.0), reverse=True)

        # Sort no-tag tasks by urgency
        no_tag_tasks.sort(key=lambda x: float(x["urgency"] or 0.0), reverse=True)

        return sorted_tags, by_tag, no_tag_tasks

    def set_filter(self, filter_text):
        """Set text filter and update lists"""
        if filter_text and filter_text.strip():
            self.filter_text = filter_text.strip()
        else:
            self.filter_text = None
        self.update_task_lists()

    def clear_filters(self):
        """Clear all filters"""
        self.filter_project = None
        self.filter_tag = None
        self.filter_text = None
        self.update_task_lists()

    def debug_filters(self):
        """Return current filter state"""
        return {
            "project_filter": self.filter_project,
            "tag_filter": self.filter_tag,
            "text_filter": self.filter_text,
            "task_count": len(self.current_tasks),
            "projects": self.projects,
            "tags": self.tags,
        }

    def set_dependency(self, task_idx, depends_on_task):
        """Set a task dependency where task_idx depends on depends_on_task"""
        if not self.current_tasks or task_idx >= len(self.current_tasks):
            return False

        task = self.current_tasks[task_idx]

        # Initialize dependencies as a set
        if "depends" not in task:
            task["depends"] = set()
        elif not isinstance(task["depends"], set):
            # Convert existing dependencies to a set if they're not already
            current_deps = task["depends"]
            if not isinstance(current_deps, list):
                current_deps = [current_deps]
            task["depends"] = set(current_deps)

        # Add the new dependency
        task["depends"].add(depends_on_task)
        task.save()
        self.update_task_lists()
        return True

    def toggle_completed(self):
        """Toggle showing/hiding completed tasks"""
        self.show_completed = not self.show_completed
        self.update_task_lists()
