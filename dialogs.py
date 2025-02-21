import curses
import curses.textpad
from datetime import datetime

class Dialogs:
    @staticmethod
    def show_help(stdscr, config):
        help_text = [
            "Tsakarori Help",
            "",
            "Navigation:",
            "  j/↓        : Move down",
            "  k/↑        : Move up",
            "  v          : Change view (all/project/tags/stats)",
            "",
            "Task Management:",
            "  a          : Add new task",
            "  e          : Edit selected task",
            "  d          : Delete selected task",
            "  Space      : Complete task",
            "",
            "Filtering:",
            "  p          : Filter by project",
            "  t          : Filter by tag",
            "  c          : Clear filters",
            "",
            "Display:",
            "  s          : Change color scheme",
            "  r          : Refresh display",
            "",
            "Other:",
            "  q          : Quit",
            "  ?          : Show this help",
            "",
            f"Current color scheme: {config.config['color_scheme']}",
            "Available schemes: " + ", ".join(config.config["color_schemes"].keys()),
            "",
            "Press any key to close help",
        ]

        height, width = stdscr.getmaxyx()
        help_win = curses.newwin(height - 2, width - 4, 1, 2)
        help_win.bkgd(" ", curses.color_pair(4))
        help_win.clear()

        for idx, line in enumerate(help_text):
            if idx < height - 3:
                help_win.addstr(idx, 0, line[: width - 6])

        help_win.refresh()
        help_win.getch()

    @staticmethod
    def add_task(stdscr, task_manager):
        curses.echo()
        height, width = stdscr.getmaxyx()
        
        # Get description
        stdscr.addstr(height - 2, 0, "Enter task description: ")
        description = stdscr.getstr().decode("utf-8")
        if not description:
            curses.noecho()
            return

        # Get project
        stdscr.addstr(height - 2, 0, "Enter project (optional): " + " " * (width - 25))
        project = stdscr.getstr().decode("utf-8")

        # Get tags
        stdscr.addstr(height - 2, 0, "Enter tags (comma-separated, optional): " + " " * (width - 35))
        tags_str = stdscr.getstr().decode("utf-8")
        tags = [t.strip() for t in tags_str.split(",")] if tags_str else None

        task_manager.add_task(description, project if project else None, tags)
        curses.noecho()

    @staticmethod
    def edit_task(stdscr, task_manager, task_idx):
        if not task_manager.current_tasks:
            return

        task = task_manager.current_tasks[task_idx]
        height, width = stdscr.getmaxyx()

        edit_win = curses.newwin(10, width - 4, height // 2 - 5, 2)
        edit_win.box()

        fields = [
            ("Description", task["description"]),
            ("Project", task["project"] or ""),
            ("Tags (comma-separated)", ",".join(task["tags"] or [])),
            ("Priority (H,M,L)", task["priority"] or ""),
            ("Due Date (YYYY-MM-DD)", str(task["due"]) if task["due"] else ""),
        ]

        current_field = 0
        while True:
            edit_win.clear()
            edit_win.box()
            edit_win.addstr(0, 2, "Edit Task (Enter to confirm, ESC to cancel)")

            for idx, (label, value) in enumerate(fields):
                if idx == current_field:
                    edit_win.attron(curses.color_pair(3))
                edit_win.addstr(idx + 1, 2, f"{label}: {value}")
                if idx == current_field:
                    edit_win.attroff(curses.color_pair(3))

            edit_win.refresh()
            key = edit_win.getch()

            if key == 27:  # ESC
                return
            elif key == ord("\n"):
                edit_win.move(current_field + 1, len(fields[current_field][0]) + 4)
                curses.echo()
                value = edit_win.getstr().decode("utf-8")
                curses.noecho()

                if value:
                    field_name = fields[current_field][0]
                    fields[current_field] = (field_name, value)
                    
                    # Update task with new value
                    if field_name == "Description":
                        task_manager.edit_task(task_idx, description=value)
                    elif field_name == "Project":
                        task_manager.edit_task(task_idx, project=value)
                    elif field_name == "Tags (comma-separated)":
                        tags = [t.strip() for t in value.split(",") if t.strip()]
                        task_manager.edit_task(task_idx, tags=tags)
                    elif field_name == "Priority (H,M,L)":
                        task_manager.edit_task(task_idx, priority=value)
                    elif field_name == "Due Date (YYYY-MM-DD)":
                        task_manager.edit_task(task_idx, due_date=value)

                current_field = (current_field + 1) % len(fields)

            elif key == curses.KEY_UP:
                current_field = (current_field - 1) % len(fields)
            elif key == curses.KEY_DOWN:
                current_field = (current_field + 1) % len(fields)

    @staticmethod
    def filter_by_project(stdscr, task_manager):
        if not task_manager.projects:
            return None

        height, width = stdscr.getmaxyx()
        win = curses.newwin(
            len(task_manager.projects) + 4,
            40,
            height // 2 - len(task_manager.projects) // 2,
            width // 2 - 20,
        )
        win.box()
        win.addstr(0, 2, "Select Project")

        selected = 0
        while True:
            for idx, project in enumerate(task_manager.projects):
                if idx == selected:
                    win.attron(curses.color_pair(3))
                win.addstr(idx + 1, 2, f"{project[:35]}")
                if idx == selected:
                    win.attroff(curses.color_pair(3))

            win.refresh()
            key = win.getch()

            if key == ord("\n"):
                return task_manager.projects[selected]
            elif key == 27:  # ESC
                return None
            elif key == curses.KEY_UP:
                selected = (selected - 1) % len(task_manager.projects)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(task_manager.projects)

    @staticmethod
    def filter_by_tag(stdscr, task_manager):
        if not task_manager.tags:
            return None

        height, width = stdscr.getmaxyx()
        win = curses.newwin(
            len(task_manager.tags) + 4,
            40,
            height // 2 - len(task_manager.tags) // 2,
            width // 2 - 20,
        )
        win.box()
        win.addstr(0, 2, "Select Tag")

        selected = 0
        while True:
            for idx, tag in enumerate(task_manager.tags):
                if idx == selected:
                    win.attron(curses.color_pair(3))
                win.addstr(idx + 1, 2, f"{tag[:35]}")
                if idx == selected:
                    win.attroff(curses.color_pair(3))

            win.refresh()
            key = win.getch()

            if key == ord("\n"):
                return task_manager.tags[selected]
            elif key == 27:  # ESC
                return None
            elif key == curses.KEY_UP:
                selected = (selected - 1) % len(task_manager.tags)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(task_manager.tags) 