#!/usr/bin/env python3
import curses
import sys
from tasklib import TaskWarrior
from datetime import datetime

class TaskWarriorTUI:
    def __init__(self):
        self.tw = TaskWarrior()
        self.current_view = "all"  # all, project, tags
        self.selected_index = 0
        self.filter_text = ""
        self.views = ["all", "by_project", "by_tags", "stats"]
        self.current_tasks = []
        self.projects = []
        self.tags = []
        self.update_task_lists()

    def update_task_lists(self):
        self.current_tasks = list(self.tw.tasks.pending())
        self.current_tasks.sort(key=lambda x: x['urgency'] or 0, reverse=True)
        self.projects = list(set(task['project'] for task in self.current_tasks if task['project']))
        self.tags = list(set(tag for task in self.current_tasks for tag in (task['tags'] or [])))

    def draw_header(self, stdscr):
        height, width = stdscr.getmaxyx()
        header = f" TaskWarrior TUI | View: {self.current_view} | Press '?' for help "
        stdscr.addstr(0, 0, header + " " * (width - len(header) - 1), curses.A_REVERSE)

    def draw_footer(self, stdscr):
        height, width = stdscr.getmaxyx()
        footer = " q:Quit | a:Add | d:Delete | e:Edit | f:Filter | v:Change View | ?:Help "
        stdscr.addstr(height - 1, 0, footer + " " * (width - len(footer) - 1), curses.A_REVERSE)

    def draw_tasks(self, stdscr):
        height, width = stdscr.getmaxyx()
        start_y = 1
        max_tasks = height - 3

        for idx, task in enumerate(self.current_tasks):
            if idx >= start_y and idx < start_y + max_tasks:
                task_str = f"{task['id']:4} {task['description'][:40]:40} "
                task_str += f"[{task['project'] or 'No Project':15}] "
                task_str += f"U:{task['urgency'] or 0:4.1f} "
                tags = ','.join(task['tags'] or [])
                task_str += f"Tags:[{tags[:15]:15}]"

                if idx == self.selected_index:
                    stdscr.addstr(idx + 1, 0, task_str[:width-1], curses.A_REVERSE)
                else:
                    stdscr.addstr(idx + 1, 0, task_str[:width-1])

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
            *[f"  - {t}" for t in self.tags]
        ]

        for idx, stat in enumerate(stats):
            if idx < height - 2:
                stdscr.addstr(idx + 1, 0, stat[:width-1])

    def show_help(self, stdscr):
        help_text = [
            "TaskWarrior TUI Help",
            "",
            "Navigation:",
            "  j/↓ : Move down",
            "  k/↑ : Move up",
            "  v   : Change view (all/project/tags/stats)",
            "",
            "Task Management:",
            "  a : Add new task",
            "  e : Edit selected task",
            "  d : Delete selected task",
            "  f : Filter tasks",
            "",
            "Other:",
            "  q : Quit",
            "  ? : Show this help",
            "",
            "Press any key to close help"
        ]

        height, width = stdscr.getmaxyx()
        for idx, line in enumerate(help_text):
            if idx < height - 1:
                stdscr.addstr(idx, 0, line[:width-1])
        stdscr.getch()

    def add_task(self, stdscr):
        curses.echo()
        height, width = stdscr.getmaxyx()
        stdscr.addstr(height-2, 0, "Enter task description: ")
        description = stdscr.getstr().decode('utf-8')
        
        if description:
            task = self.tw.tasks.add(description)
            stdscr.addstr(height-2, 0, "Enter project (optional): ")
            project = stdscr.getstr().decode('utf-8')
            if project:
                task['project'] = project

            stdscr.addstr(height-2, 0, "Enter tags (comma-separated, optional): ")
            tags = stdscr.getstr().decode('utf-8')
            if tags:
                task['tags'] = [t.strip() for t in tags.split(',')]

            task.save()
            self.update_task_lists()
        
        curses.noecho()

    def main(self, stdscr):
        curses.curs_set(0)
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
            if key == ord('q'):
                break
            elif key == ord('j') or key == curses.KEY_DOWN:
                self.selected_index = min(self.selected_index + 1, len(self.current_tasks) - 1)
            elif key == ord('k') or key == curses.KEY_UP:
                self.selected_index = max(self.selected_index - 1, 0)
            elif key == ord('v'):
                current_idx = self.views.index(self.current_view)
                self.current_view = self.views[(current_idx + 1) % len(self.views)]
            elif key == ord('a'):
                self.add_task(stdscr)
            elif key == ord('?'):
                self.show_help(stdscr)
            elif key == ord('d') and self.current_tasks:
                self.current_tasks[self.selected_index].delete()
                self.update_task_lists()
                self.selected_index = min(self.selected_index, len(self.current_tasks) - 1)

def main():
    app = TaskWarriorTUI()
    curses.wrapper(app.main)

if __name__ == "__main__":
    main() 