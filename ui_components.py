import curses


class UIComponents:
    @staticmethod
    def draw_header(stdscr, current_view, task_manager):
        height, width = stdscr.getmaxyx()

        # Build filter info
        filters = []
        if task_manager.filter_project:
            filters.append(f"Project:{task_manager.filter_project}")
        if task_manager.filter_tag:
            filters.append(f"Tag:{task_manager.filter_tag}")
        if task_manager.filter_text:
            filters.append(f"Text:{task_manager.filter_text}")

        filter_str = " | Filters: " + ", ".join(filters) if filters else ""
        header = f" Tsakarori | View: {current_view}{filter_str} | Press '?' for help "

        stdscr.attron(curses.color_pair(1))
        stdscr.addstr(0, 0, header + " " * (width - len(header) - 1))
        stdscr.attroff(curses.color_pair(1))

    @staticmethod
    def draw_footer(stdscr):
        height, width = stdscr.getmaxyx()
        footer = " q:Quit | a:Add | d:Add dependency | D:Delete | e:Edit | f:Filter | v:Change View | ?:Help "
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(height - 1, 0, footer + " " * (width - len(footer) - 1))
        stdscr.attroff(curses.color_pair(2))

    @staticmethod
    def draw_task_list(stdscr, current_tasks, selected_index):
        height, width = stdscr.getmaxyx()
        list_width = width // 2
        start_y = 0
        max_tasks = height - 2

        # Draw vertical separator
        for y in range(1, height - 1):
            stdscr.addstr(y, list_width, "│")

        # Tasks are already sorted by urgency in TaskManager
        # Draw task list
        for idx, task in enumerate(current_tasks):
            if idx >= start_y and idx < start_y + max_tasks:
                # Format task info
                desc_width = 30
                task_id = f"{task['id']:4}"
                description = f"{task['description'][:desc_width]:<{desc_width}}"

                # Format metadata
                urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                project = task["project"] or "None"
                tags = ",".join(task["tags"] or [])
                metadata = f" ({urgency}, {project}, [{tags}])"

                # Truncate metadata if too long
                available_width = list_width - len(task_id) - len(description) - 2
                if len(metadata) > available_width:
                    metadata = metadata[: available_width - 3] + "...)"

                task_str = task_id + ". " + description + metadata

                # Determine if task is completed
                is_completed = task["status"] == "completed"

                if idx == selected_index:
                    if is_completed:
                        stdscr.attron(curses.color_pair(3) | curses.A_DIM)
                    else:
                        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                    # Fill entire line width with selection color
                    stdscr.addstr(idx + 2, 0, " " * (list_width))
                    # Draw task info
                    stdscr.addstr(idx + 2, 0, task_str)
                    if is_completed:
                        stdscr.attroff(curses.color_pair(3) | curses.A_DIM)
                    else:
                        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                else:
                    if is_completed:
                        stdscr.attron(curses.color_pair(4) | curses.A_DIM)
                    else:
                        stdscr.attron(curses.color_pair(4))
                    stdscr.addstr(idx + 2, 0, task_str)
                    if is_completed:
                        stdscr.attroff(curses.color_pair(4) | curses.A_DIM)
                    else:
                        stdscr.attroff(curses.color_pair(4))

    @staticmethod
    def draw_task_details(stdscr, task, selected_index, task_manager):
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
            f"Due: {task['due'] or 'None'}",
            "",
            "Depends on:",
        ]

        # Add dependencies if they exist
        blocked_by = []
        
        # Get dependencies from task._data
        depends = task._data.get('depends', None)
        if depends and hasattr(depends, '_data'):  # Handle LazyUUIDTaskSet
            # Get the UUIDs from the LazyUUIDTaskSet
            dep_uuids = depends._data
            if dep_uuids:
                # Find tasks that this task depends on
                for t in task_manager.tw.tasks:
                    if str(t._data.get('uuid', '')) in [str(uuid) for uuid in dep_uuids]:
                        project_info = f" [{t['project']}]" if t['project'] else ""
                        blocked_by.append(f"  - {t['description']}{project_info}")
        
        if blocked_by:
            details.extend(blocked_by)
        else:
            details.append("  None")

        # Debug info
        details.extend([
            "",
            "Debug info:",
            f"  depends: {depends}",
            f"  depends._data: {depends._data if hasattr(depends, '_data') else None}",
            f"  task._data: {task._data}",
        ])

        for idx, detail in enumerate(details):
            if idx + 2 < height - 1:  # Leave space for header and footer
                if (
                    detail.startswith("Project:")
                    or detail.startswith("Tags:")
                    or detail == "Description:"
                    or detail == "Depends on:"
                    or detail == "Debug info:"
                ):
                    stdscr.attron(curses.color_pair(5))
                    stdscr.addstr(idx + 2, detail_x + 1, detail[:detail_width])
                    stdscr.attroff(curses.color_pair(5))
                else:
                    stdscr.addstr(idx + 2, detail_x + 1, detail[:detail_width])

    @staticmethod
    def draw_task_list_by_project(stdscr, task_manager, selected_index):
        height, width = stdscr.getmaxyx()
        list_width = width // 2

        # Draw vertical separator
        for y in range(1, height - 1):
            stdscr.addstr(y, list_width, "│")

        # Get tasks organized by project
        projects, by_project, no_project_tasks = task_manager.get_tasks_by_project()

        current_y = 2  # Start below header
        current_index = 0
        selected_task = None  # Track the selected task

        # Draw projects and their tasks
        for project in projects:
            # Draw project header
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(current_y, 0, f"Project: {project}")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            current_y += 1

            # Draw tasks for this project
            for task in by_project[project]:
                if current_y < height - 1:  # Leave space for footer
                    desc_width = 30
                    task_id = f"{task['id']:4}"
                    description = f"{task['description'][:desc_width]:<{desc_width}}"
                    urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                    tags = ",".join(task["tags"] or [])
                    metadata = f" ({urgency}, [{tags}])"

                    available_width = list_width - len(task_id) - len(description) - 2
                    if len(metadata) > available_width:
                        metadata = metadata[: available_width - 3] + "...)"

                    task_str = task_id + ". " + description + metadata

                    if current_index == selected_index:
                        selected_task = task  # Store the selected task
                        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                        stdscr.addstr(current_y, 0, " " * (list_width))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                    else:
                        stdscr.attron(curses.color_pair(4))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(4))

                current_y += 1
                current_index += 1

        # Draw tasks with no project
        if no_project_tasks and current_y < height - 1:
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(current_y, 0, "No Project")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            current_y += 1

            for task in no_project_tasks:
                if current_y < height - 1:
                    desc_width = 30
                    task_id = f"{task['id']:4}"
                    description = f"{task['description'][:desc_width]:<{desc_width}}"
                    urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                    tags = ",".join(task["tags"] or [])
                    metadata = f" ({urgency}, [{tags}])"

                    available_width = list_width - len(task_id) - len(description) - 2
                    if len(metadata) > available_width:
                        metadata = metadata[: available_width - 3] + "...)"

                    task_str = task_id + ". " + description + metadata

                    if current_index == selected_index:
                        selected_task = task  # Store the selected task
                        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                        stdscr.addstr(current_y, 0, " " * (list_width))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                    else:
                        stdscr.attron(curses.color_pair(4))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(4))

                current_y += 1
                current_index += 1

        return selected_task

    @staticmethod
    def draw_task_list_by_tag(stdscr, task_manager, selected_index):
        height, width = stdscr.getmaxyx()
        list_width = width // 2

        # Draw vertical separator
        for y in range(1, height - 1):
            stdscr.addstr(y, list_width, "│")

        # Get tasks organized by tag
        tags, by_tag, no_tag_tasks = task_manager.get_tasks_by_tag()

        current_y = 2  # Start below header
        current_index = 0
        selected_task = None  # Track the selected task

        # Draw tags and their tasks
        for tag in tags:
            # Draw tag header
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(current_y, 0, f"Tag: {tag}")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            current_y += 1

            # Draw tasks for this tag
            for task in by_tag[tag]:
                if current_y < height - 1:  # Leave space for footer
                    desc_width = 30
                    task_id = f"{task['id']:4}"
                    description = f"{task['description'][:desc_width]:<{desc_width}}"
                    urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                    project = task["project"] or "None"
                    metadata = f" ({urgency}, {project})"

                    available_width = list_width - len(task_id) - len(description) - 2
                    if len(metadata) > available_width:
                        metadata = metadata[: available_width - 3] + "...)"

                    task_str = task_id + ". " + description + metadata

                    if current_index == selected_index:
                        selected_task = task  # Store the selected task
                        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                        stdscr.addstr(current_y, 0, " " * (list_width))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                    else:
                        stdscr.attron(curses.color_pair(4))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(4))

                current_y += 1
                current_index += 1

        # Draw tasks with no tags
        if no_tag_tasks and current_y < height - 1:
            stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
            stdscr.addstr(current_y, 0, "No Tags")
            stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)
            current_y += 1

            for task in no_tag_tasks:
                if current_y < height - 1:
                    desc_width = 30
                    task_id = f"{task['id']:4}"
                    description = f"{task['description'][:desc_width]:<{desc_width}}"
                    urgency = f"U:{float(task['urgency'] or 0):4.1f}"
                    project = task["project"] or "None"
                    metadata = f" ({urgency}, {project})"

                    available_width = list_width - len(task_id) - len(description) - 2
                    if len(metadata) > available_width:
                        metadata = metadata[: available_width - 3] + "...)"

                    task_str = task_id + ". " + description + metadata

                    if current_index == selected_index:
                        selected_task = task  # Store the selected task
                        stdscr.attron(curses.color_pair(3) | curses.A_BOLD)
                        stdscr.addstr(current_y, 0, " " * (list_width))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(3) | curses.A_BOLD)
                    else:
                        stdscr.attron(curses.color_pair(4))
                        stdscr.addstr(current_y, 0, task_str)
                        stdscr.attroff(curses.color_pair(4))

                current_y += 1
                current_index += 1

        return selected_task

    @staticmethod
    def draw_tasks(stdscr, current_tasks, selected_index, current_view, task_manager):
        if not current_tasks:
            return

        selected_task = None
        if current_view == "by_project":
            selected_task = UIComponents.draw_task_list_by_project(
                stdscr, task_manager, selected_index
            )
            if selected_task:
                UIComponents.draw_task_details(stdscr, selected_task, selected_index, task_manager)
        elif current_view == "by_tags":
            selected_task = UIComponents.draw_task_list_by_tag(
                stdscr, task_manager, selected_index
            )
            if selected_task:
                UIComponents.draw_task_details(stdscr, selected_task, selected_index, task_manager)
        else:
            UIComponents.draw_task_list(stdscr, current_tasks, selected_index)
            if selected_index < len(current_tasks):
                UIComponents.draw_task_details(
                    stdscr, current_tasks[selected_index], selected_index, task_manager
                )

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
