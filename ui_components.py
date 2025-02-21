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
    def draw_tasks(stdscr, current_tasks, selected_index):
        height, width = stdscr.getmaxyx()
        start_y = 1
        max_tasks = height - 3

        stdscr.attron(curses.color_pair(4))
        for idx, task in enumerate(current_tasks):
            if idx >= start_y and idx < start_y + max_tasks:
                task_str = f"{task['id']:4} {task['description'][:40]:40} "
                
                # Highlight project
                project_str = f"[{task['project'] or 'No Project':15}]"
                urgency_str = f" U:{task['urgency'] or 0:4.1f} "
                
                # Highlight tags
                tags = ",".join(task["tags"] or [])
                tags_str = f"Tags:[{tags[:15]:15}]"

                if idx == selected_index:
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(idx + 1, 0, task_str)
                    stdscr.attron(curses.color_pair(5))  # Use highlight color for project
                    stdscr.addstr(idx + 1, len(task_str), project_str)
                    stdscr.attroff(curses.color_pair(5))
                    stdscr.attron(curses.color_pair(3))
                    stdscr.addstr(idx + 1, len(task_str) + len(project_str), urgency_str)
                    stdscr.attron(curses.color_pair(5))  # Use highlight color for tags
                    stdscr.addstr(idx + 1, len(task_str) + len(project_str) + len(urgency_str), tags_str)
                    stdscr.attroff(curses.color_pair(5))
                    stdscr.attroff(curses.color_pair(3))
                else:
                    stdscr.addstr(idx + 1, 0, task_str)
                    stdscr.attron(curses.color_pair(5))  # Use highlight color for project
                    stdscr.addstr(idx + 1, len(task_str), project_str)
                    stdscr.attroff(curses.color_pair(5))
                    stdscr.addstr(idx + 1, len(task_str) + len(project_str), urgency_str)
                    stdscr.attron(curses.color_pair(5))  # Use highlight color for tags
                    stdscr.addstr(idx + 1, len(task_str) + len(project_str) + len(urgency_str), tags_str)
                    stdscr.attroff(curses.color_pair(5))
        stdscr.attroff(curses.color_pair(4))

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
                    stdscr.attron(curses.color_pair(5))  # Highlight section headers
                    stdscr.addstr(idx + 1, 0, stat[: width - 1])
                    stdscr.attroff(curses.color_pair(5))
                else:
                    stdscr.addstr(idx + 1, 0, stat[: width - 1])
        stdscr.attroff(curses.color_pair(4)) 