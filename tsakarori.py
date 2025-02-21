#!/usr/bin/env python3
import curses
import sys
from tasklib import TaskWarrior, Task
from datetime import datetime
import tsakarori_config
import curses.textpad


class TsakaroriTUI:
    def __init__(self):
        self.tw = TaskWarrior()
        self.current_view = "all"  # all, project, tags
        self.selected_index = 0
        self.filter_text = ""
        self.views = ["all", "by_project", "by_tags", "stats"]
        self.current_tasks = []
        self.projects = []
        self.tags = []
        self.config = tsakarori_config.Config()
        self.filter_project = None
        self.filter_tag = None
        self.update_task_lists()

    def update_task_lists(self):
        tasks = self.tw.tasks.pending()

        if self.filter_project:
            tasks = [t for t in tasks if t["project"] == self.filter_project]
        if self.filter_tag:
            tasks = [t for t in tasks if self.filter_tag in (t["tags"] or [])]

        self.current_tasks = list(tasks)
        self.current_tasks.sort(key=lambda x: x["urgency"] or 0, reverse=True)
        self.projects = list(
            set(task["project"] for task in self.current_tasks if task["project"])
        )
        self.tags = list(
            set(tag for task in self.current_tasks for tag in (task["tags"] or []))
        )

    def draw_header(self, stdscr):
        height, width = stdscr.getmaxyx()
        header = f" Tsakarori | View: {self.current_view} | Press '?' for help "
        stdscr.addstr(0, 0, header + " " * (width - len(header) - 1), curses.A_REVERSE)

    def draw_footer(self, stdscr):
        height, width = stdscr.getmaxyx()
        footer = (
            " q:Quit | a:Add | d:Delete | e:Edit | f:Filter | v:Change View | ?:Help "
        )
        stdscr.addstr(
            height - 1, 0, footer + " " * (width - len(footer) - 1), curses.A_REVERSE
        )

    def draw_tasks(self, stdscr):
        height, width = stdscr.getmaxyx()
        start_y = 1
        max_tasks = height - 3

        for idx, task in enumerate(self.current_tasks):
            if idx >= start_y and idx < start_y + max_tasks:
                task_str = f"{task['id']:4} {task['description'][:40]:40} "
                task_str += f"[{task['project'] or 'No Project':15}] "
                task_str += f"U:{task['urgency'] or 0:4.1f} "
                tags = ",".join(task["tags"] or [])
                task_str += f"Tags:[{tags[:15]:15}]"

                if idx == self.selected_index:
                    stdscr.addstr(idx + 1, 0, task_str[: width - 1], curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, task_str[: width - 1])

    def draw_stats(self, stdscr):
        height, width = stdscr.getmaxyx()
        pending = len(self.tw.tasks.pending())
        completed = len(self.tw.tasks.completed())

        stats = [
            f"Total pending tasks: {pending}",
            f"Total completed tasks: {completed}",
            f"Number of projects: {len(self.projects)}",
            f"Number of tags: {len(self.tags)}",
            "",
            "Projects:",
            *[f"  - {p}" for p in self.projects],
            "",
            "Tags:",
            *[f"  - {t}" for t in self.tags],
        ]

        for idx, stat in enumerate(stats):
            if idx < height - 2:
                stdscr.addstr(idx + 1, 0, stat[: width - 1])

    def show_help(self, stdscr):
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
            f"Current color scheme: {self.config.config['color_scheme']}",
            "Available schemes: "
            + ", ".join(self.config.config["color_schemes"].keys()),
            "",
            "Press any key to close help",
        ]

        height, width = stdscr.getmaxyx()
        help_win = curses.newwin(height - 2, width - 4, 1, 2)
        help_win.attron(curses.color_pair(4))

        for idx, line in enumerate(help_text):
            if idx < height - 3:
                help_win.addstr(idx, 0, line[: width - 6])

        help_win.refresh()
        help_win.getch()

    def add_task(self, stdscr):
        curses.echo()
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height - 2, 0, "Enter task description: ")
        description = stdscr.getstr().decode("utf-8")

        if description:
            # Create a new Task object instead of using add()
            task = Task(self.tw)
            task["description"] = description

            stdscr.addstr(
                height - 2, 0, "Enter project (optional): " + " " * (width - 25)
            )
            project = stdscr.getstr().decode("utf-8")
            if project:
                task["project"] = project

            stdscr.addstr(
                height - 2,
                0,
                "Enter tags (comma-separated, optional): " + " " * (width - 35),
            )
            tags = stdscr.getstr().decode("utf-8")
            if tags:
                task["tags"] = [t.strip() for t in tags.split(",")]

            # Save the new task
            task.save()
            self.update_task_lists()

        curses.noecho()

    def edit_task(self, stdscr):
        if not self.current_tasks:
            return

        task = self.current_tasks[self.selected_index]
        height, width = stdscr.getmaxyx()

        # Create a sub-window for editing
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
                # Edit current field
                edit_win.move(current_field + 1, len(fields[current_field][0]) + 4)
                curses.echo()
                value = edit_win.getstr().decode("utf-8")
                curses.noecho()

                field_name = fields[current_field][0]
                if value:
                    if field_name == "Description":
                        task["description"] = value
                    elif field_name == "Project":
                        task["project"] = value
                    elif field_name == "Tags (comma-separated)":
                        task["tags"] = [
                            t.strip() for t in value.split(",") if t.strip()
                        ]
                    elif field_name == "Priority (H,M,L)":
                        if value.upper() in ["H", "M", "L"]:
                            task["priority"] = value.upper()
                    elif field_name == "Due Date (YYYY-MM-DD)":
                        try:
                            task["due"] = datetime.strptime(value, "%Y-%m-%d")
                        except ValueError:
                            pass

                fields[current_field] = (fields[current_field][0], value)
                current_field = (current_field + 1) % len(fields)

            elif key == curses.KEY_UP:
                current_field = (current_field - 1) % len(fields)
            elif key == curses.KEY_DOWN:
                current_field = (current_field + 1) % len(fields)

        task.save()
        self.update_task_lists()

    def change_color_scheme(self, stdscr):
        schemes = list(self.config.config["color_schemes"].keys())
        current_idx = schemes.index(self.config.config["color_scheme"])
        new_scheme = schemes[(current_idx + 1) % len(schemes)]
        self.config.config["color_scheme"] = new_scheme
        self.config.save_config()
        self.setup_colors()

        # Force full UI refresh
        stdscr.clear()
        self.draw_header(stdscr)
        self.draw_footer(stdscr)
        stdscr.refresh()

        # Show temporary status message
        height, width = stdscr.getmaxyx()
        status_msg = f"Color scheme: {new_scheme}"
        stdscr.addstr(height // 2, (width - len(status_msg)) // 2, status_msg, curses.A_REVERSE)
        stdscr.refresh()
        curses.napms(500)  # Show message for 500ms

    def filter_by_project(self, stdscr):
        if not self.projects:
            return

        height, width = stdscr.getmaxyx()
        win = curses.newwin(
            len(self.projects) + 4,
            40,
            height // 2 - len(self.projects) // 2,
            width // 2 - 20,
        )
        win.box()
        win.addstr(0, 2, "Select Project")

        selected = 0
        while True:
            for idx, project in enumerate(self.projects):
                if idx == selected:
                    win.attron(curses.color_pair(3))
                win.addstr(idx + 1, 2, f"{project[:35]}")
                if idx == selected:
                    win.attroff(curses.color_pair(3))

            win.refresh()
            key = win.getch()

            if key == ord("\n"):
                self.filter_project = self.projects[selected]
                break
            elif key == 27:  # ESC
                break
            elif key == curses.KEY_UP:
                selected = (selected - 1) % len(self.projects)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(self.projects)

        self.update_task_lists()

    def filter_by_tag(self, stdscr):
        if not self.tags:
            return

        height, width = stdscr.getmaxyx()
        win = curses.newwin(
            len(self.tags) + 4, 40, height // 2 - len(self.tags) // 2, width // 2 - 20
        )
        win.box()
        win.addstr(0, 2, "Select Tag")

        selected = 0
        while True:
            for idx, tag in enumerate(self.tags):
                if idx == selected:
                    win.attron(curses.color_pair(3))
                win.addstr(idx + 1, 2, f"{tag[:35]}")
                if idx == selected:
                    win.attroff(curses.color_pair(3))

            win.refresh()
            key = win.getch()

            if key == ord("\n"):
                self.filter_tag = self.tags[selected]
                break
            elif key == 27:  # ESC
                break
            elif key == curses.KEY_UP:
                selected = (selected - 1) % len(self.tags)
            elif key == curses.KEY_DOWN:
                selected = (selected + 1) % len(self.tags)

        self.update_task_lists()

    def setup_colors(self):
        curses.start_color()
        curses.use_default_colors()

        colors = self.config.get_color_pairs()
        curses.init_pair(1, colors["header"][0], colors["header"][1])
        curses.init_pair(2, colors["footer"][0], colors["footer"][1])
        curses.init_pair(3, colors["selected"][0], colors["selected"][1])
        curses.init_pair(4, colors["normal"][0], colors["normal"][1])
        curses.init_pair(5, colors["highlight"][0], colors["highlight"][1])

    def main(self, stdscr):
        curses.curs_set(0)
        self.setup_colors()
        stdscr.clear()

        while True:
            stdscr.clear()
            self.draw_header(stdscr)

            if self.current_view == "stats":
                self.draw_stats(stdscr)
            else:
                self.draw_tasks(stdscr)

            self.draw_footer(stdscr)
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == ord("j") or key == curses.KEY_DOWN:
                self.selected_index = min(
                    self.selected_index + 1, len(self.current_tasks) - 1
                )
            elif key == ord("k") or key == curses.KEY_UP:
                self.selected_index = max(self.selected_index - 1, 0)
            elif key == ord("v"):
                current_idx = self.views.index(self.current_view)
                self.current_view = self.views[(current_idx + 1) % len(self.views)]
            elif key == ord("a"):
                self.add_task(stdscr)
            elif key == ord("?"):
                self.show_help(stdscr)
            elif key == ord("d") and self.current_tasks:
                self.current_tasks[self.selected_index].delete()
                self.update_task_lists()
                self.selected_index = min(
                    self.selected_index, len(self.current_tasks) - 1
                )
            elif key == ord("e"):
                self.edit_task(stdscr)
            elif key == ord("s"):
                self.change_color_scheme(stdscr)
            elif key == ord("p"):
                self.filter_by_project(stdscr)
            elif key == ord("t"):
                self.filter_by_tag(stdscr)
            elif key == ord("c"):
                self.filter_project = None
                self.filter_tag = None
                self.update_task_lists()
            elif key == ord(" ") and self.current_tasks:
                self.current_tasks[self.selected_index].done()
                self.update_task_lists()


def main():
    app = TsakaroriTUI()
    curses.wrapper(app.main)


if __name__ == "__main__":
    main()
