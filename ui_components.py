import curses

class UIComponents:
    @staticmethod
    def draw_header(stdscr, current_view):
        height, width = stdscr.getmaxyx()
        header = f" Tsakarori | View: {current_view} | Press '?' for help "
        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, header + " " * (width - len(header) - 1))
        stdscr.attroff(curses.color_pair(1))

    @staticmethod
    def draw_footer(stdscr):
        height, width = stdscr.getmaxyx()
        footer = " q:Quit | a:Add | d:Delete | e:Edit | f:Filter | v:Change View | ?:Help "
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(height - 1, 0, footer + " " * (width - len(footer) - 1))
        stdscr.attroff(curses.color_pair(2))

    @staticmethod
    def draw_task_list(stdscr, current_tasks, selected_index):
        height, width = stdscr.getmaxyx()
        list_width = width // 2
        start_y = 1
        max_tasks = height - 3

        # Draw vertical separator
        for y in range(1, height - 1):
            stdscr.addstr(y, list_width, "│")

        # Sort tasks by urgency (highest to lowest)
        sorted_tasks = sorted(current_tasks, key=lambda x: float(x['urgency'] or 0), reverse=True)

        # Draw task list
        for idx, task in enumerate(sorted_tasks):
            if idx >= start_y and idx < start_y + max_tasks:
                # Format task info
                desc_width = 30
                task_id = f"{task['id']:4}"
                description = f"{task['description'][:desc_width]:<{desc_width}}"
                
                # Format metadata
                urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                project = task['project'] or 'None'
                tags = ",".join(task["tags"] or [])
                metadata = f" ({urgency}, {project}, [{tags}])"
                
                # Truncate metadata if too long
                available_width = list_width - len(task_id) - len(description) - 2
                if len(metadata) > available_width:
                    metadata = metadata[:available_width-3] + "...)"
                
                task_str = task_id + description + metadata
                
                if idx == selected_index:
                    stdscr.attron(curses.color_pair(3) | curses.A_BOLD)  # Selection color + bold
                    # Fill entire line width with selection color
                    stdscr.addstr(idx + 1, 0, " " * (list_width))
                    # Draw task info
                    stdscr.addstr(idx + 1, 0, task_str)
                    stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                else:
                    stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(idx + 1, 0, task_str)
                    stdscr.attroff(curses.color_pair(4))

    @staticmethod
    def draw_task_details(stdscr, task, selected_index):
        if task is None:
            return

        height, width = stdscr.getmaxyx()
        detail_x = (width // 2) + 1
        detail_width = width - detail_x - 1

        # Draw details header
        stdscr.attron(curses.color_pair(5))
        stdscr.addstr(1, detail_x + 1, "Task Details")
        stdscr.attroff(curses.color_pair(5))

        # Draw task details
        details = [
            "",
            f"ID: {task['id']}",
            "",
            "Description:",
            f"{task['description']}",
            "",
            f"Project: {task['project'] or 'None'}",
            "",
            "Tags:",
            ", ".join(task["tags"] or ["None"]),
            "",
            f"Urgency: {task['urgency'] or 0:.1f}",
            "",
            f"Priority: {task['priority'] or 'None'}",
            "",
            f"Due: {task['due'] or 'None'}"
        ]

        for idx, detail in enumerate(details):
            if idx + 2 < height - 1:  # Leave space for header and footer
                if detail.startswith("Project:") or detail.startswith("Tags:") or detail == "Description:":
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addstr(idx + 2, detail_x + 1, detail[:detail_width])
                    stdscr.attroff(curses.color_pair(5))
                else:
                    stdscr.addstr(idx + 2, detail_x + 1, detail[:detail_width])

    @staticmethod
    def draw_tasks(stdscr, current_tasks, selected_index):
        if not current_tasks:
            return
            
        UIComponents.draw_task_list(stdscr, current_tasks, selected_index)
        if selected_index < len(current_tasks):
            UIComponents.draw_task_details(stdscr, current_tasks[selected_index], selected_index)

    @staticmethod
    def draw_stats(stdscr, task_manager):
        height, width = stdscr.getmaxyx()
        pending = len(task_manager.tw.tasks.pending())
        completed = len(task_manager.tw.tasks.completed())

        stats = [
            f"Total pending tasks: {pending}",
            f"Total completed tasks: {completed}",
            f"Number of projects: {len(task_manager.projects)}",
            f"Number of tags: {len(task_manager.tags)}",
            "",
            "Projects:",
            *[f"  - {p}" for p in task_manager.projects],
            "",
            "Tags:",
            *[f"  - {t}" for t in task_manager.tags],
        ]

        stdscr.attron(curses.color_pair(4))
        for idx, stat in enumerate(stats):
            if idx < height - 2:
                if stat.startswith("Projects:") or stat.startswith("Tags:"):
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addstr(idx + 1, 0, stat[: width - 1])
                    stdscr.attroff(curses.color_pair(5))
                else:
                    stdscr.addstr(idx + 1, 0, stat[: width - 1])
        stdscr.attroff(curses.color_pair(4)) 