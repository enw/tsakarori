import curses
import curses.textpad
from datetime import datetime
from task_service import TaskService


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
            "  D          : Delete selected task",
            "  d          : Add dependency to selected task (Space to select)",
            "  Space      : Complete task",
            "",
            "Filtering:",
            "  p          : Filter by project",
            "  t          : Filter by tag",
            "  T          : Toggle show/hide completed tasks",
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
        stdscr.addstr(
            height - 2,
            0,
            "Enter tags (comma-separated, optional): " + " " * (width - 35),
        )
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
        edit_win.keypad(True)  # Enable keypad for arrow keys

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
            edit_win.addstr(
                0, 2, "Edit Task (Enter to edit, d to delete value, ESC to cancel)"
            )

            # Draw all fields, highlighting the current one
            for idx, (label, value) in enumerate(fields):
                if idx == current_field:
                    edit_win.attron(curses.color_pair(3) | curses.A_BOLD)
                edit_win.addstr(idx + 1, 2, f"{label}: {value}")
                if idx == current_field:
                    edit_win.attroff(curses.color_pair(3) | curses.A_BOLD)

            edit_win.refresh()
            key = edit_win.getch()

            if key == 27:  # ESC
                return
            elif key == ord("D"):  # Delete field value
                field_name = fields[current_field][0]
                fields[current_field] = (field_name, "")

                # Update task with empty value
                if field_name == "Description":
                    # Don't allow empty description
                    continue
                elif field_name == "Project":
                    task_manager.edit_task(task_idx, project=None)
                elif field_name == "Tags (comma-separated)":
                    task_manager.edit_task(task_idx, tags=[])
                elif field_name == "Priority (H,M,L)":
                    task_manager.edit_task(task_idx, priority=None)
                elif field_name == "Due Date (YYYY-MM-DD)":
                    task_manager.edit_task(task_idx, due_date=None)
            elif key == ord("\n"):  # Enter
                # Clear the line for input
                edit_win.move(current_field + 1, len(fields[current_field][0]) + 4)
                edit_win.clrtoeol()
                edit_win.box()  # Restore the box
                edit_win.move(current_field + 1, len(fields[current_field][0]) + 4)

                # Get input
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
                        if value.upper() in ["H", "M", "L"]:
                            task_manager.edit_task(task_idx, priority=value.upper())
                    elif field_name == "Due Date (YYYY-MM-DD)":
                        try:
                            datetime.strptime(value, "%Y-%m-%d")
                            task_manager.edit_task(task_idx, due_date=value)
                        except ValueError:
                            # Show error message
                            edit_win.addstr(
                                current_field + 1,
                                len(fields[current_field][0]) + len(value) + 5,
                                " (Invalid date format)",
                                curses.color_pair(5) | curses.A_BOLD,
                            )
                            edit_win.refresh()
                            curses.napms(1000)  # Show error for 1 second

            elif key == curses.KEY_UP:
                current_field = (current_field - 1) % len(fields)
            elif key == curses.KEY_DOWN:
                current_field = (current_field + 1) % len(fields)
            elif key == ord("j"):  # Also allow j/k navigation
                current_field = (current_field + 1) % len(fields)
            elif key == ord("k"):
                current_field = (current_field - 1) % len(fields)

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

    @staticmethod
    def filter_tasks(stdscr):
        height, width = stdscr.getmaxyx()

        # Create filter window
        filter_win = curses.newwin(5, width - 4, height // 2 - 2, 2)
        filter_win.box()
        filter_win.addstr(0, 2, "Filter Tasks")
        filter_win.addstr(1, 2, "Enter text to filter by description, project, or tags")
        filter_win.addstr(2, 2, "Press Ctrl-G or Enter to apply, ESC to cancel")

        # Create text input box
        text_win = curses.newwin(1, width - 8, height // 2 + 1, 4)
        text_box = curses.textpad.Textbox(text_win, insert_mode=True)

        # Show cursor for text input
        curses.curs_set(1)

        # Get filter text
        filter_win.refresh()
        text_win.refresh()

        try:
            # Handle ESC key
            while True:
                c = stdscr.getch()
                if c == 27:  # ESC
                    curses.curs_set(0)
                    return None
                if c == ord("\n") or c == ord("\r"):
                    break
                text_box.do_command(c)
                text_win.refresh()

            filter_text = text_box.gather().strip()
            curses.curs_set(0)
            return filter_text if filter_text else None

        finally:
            curses.curs_set(0)

    @staticmethod
    def select_dependency(stdscr, task_manager, current_task_idx):
        """Select a task to depend on"""
        if not task_manager.current_tasks:
            return None

        height, width = stdscr.getmaxyx()
        # Create a list of tasks excluding the current task
        available_tasks = [
            t for i, t in enumerate(task_manager.current_tasks) if i != current_task_idx
        ]

        if not available_tasks:
            return None

        win = curses.newwin(
            len(available_tasks) + 4,
            width - 4,
            height // 2 - len(available_tasks) // 2,
            2,
        )
        win.keypad(True)  # Enable keypad for arrow keys
        win.box()
        win.addstr(0, 2, "Select Task to Depend On (Space to select, ESC to cancel)")
        win.addstr(1, 2, "Use ↑/↓ or j/k to navigate")

        selected = 0
        while True:
            for idx, task in enumerate(available_tasks):
                # Calculate available width for the task string
                available_width = width - 12  # Account for borders and padding

                # Format task ID and project info
                task_id = f"{task['id']:4}"
                project_info = f" [{task['project']}]" if task["project"] else ""

                # Calculate remaining width for description
                desc_width = (
                    available_width - len(task_id) - len(project_info) - 2
                )  # -2 for ". "
                description = task["description"][:desc_width]

                # Build the task string with proper padding
                task_str = f"{task_id}. {description:<{desc_width}}{project_info}"

                if idx == selected:
                    win.attron(curses.color_pair(3))
                win.addstr(idx + 2, 2, task_str)
                if idx == selected:
                    win.attroff(curses.color_pair(3))

            win.refresh()
            key = win.getch()

            if key == ord(" "):  # Space to select
                return available_tasks[selected]
            elif key == 27:  # ESC
                return None
            elif key == curses.KEY_UP or key == ord("k"):
                selected = (selected - 1) % len(available_tasks)
            elif key == curses.KEY_DOWN or key == ord("j"):
                selected = (selected + 1) % len(available_tasks)


class TaskDialog:
    def __init__(self):
        self.task_service = TaskService()
    
    def validate_input(self, description: str) -> bool:
        """Validate task input"""
        try:
            # Use service validation
            self.task_service.add_task(description)
            return True
        except ValueError:
            return False
    
    def validate_due_date(self, date_str: str) -> bool:
        """Validate due date format"""
        try:
            self.task_service.add_task("test", due=date_str)
            return True
        except ValueError:
            return False
