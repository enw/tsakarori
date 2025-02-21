#!/usr/bin/env python3
import curses
from models import TaskManager
from ui_components import UIComponents
from dialogs import Dialogs
import tsakarori_config


class TsakaroriTUI:
    def __init__(self):
        self.task_manager = TaskManager()
        self.current_view = "all"
        self.selected_index = 0
        self.views = ["all", "by_project", "by_tags", "stats"]
        self.config = tsakarori_config.Config()

    def setup_colors(self):
        curses.start_color()
        curses.use_default_colors()

        for i in range(1, 6):
            curses.init_pair(i, -1, -1)

        colors = self.config.get_color_pairs()
        curses.init_pair(1, colors["header"][0], colors["header"][1])
        curses.init_pair(2, colors["footer"][0], colors["footer"][1])
        curses.init_pair(3, colors["selected"][0], colors["selected"][1])
        curses.init_pair(4, colors["normal"][0], colors["normal"][1])
        curses.init_pair(5, colors["highlight"][0], colors["highlight"][1])

    def change_color_scheme(self, stdscr):
        schemes = list(self.config.config["color_schemes"].keys())
        current_idx = schemes.index(self.config.config["color_scheme"])
        new_scheme = schemes[(current_idx + 1) % len(schemes)]
        self.config.config["color_scheme"] = new_scheme
        self.config.save_config()

        # Reset and reinitialize colors
        self.setup_colors()

        # Force complete screen redraw
        stdscr.clear()
        stdscr.refresh()

        # Show temporary status message
        height, width = stdscr.getmaxyx()
        status_msg = f"Color scheme: {new_scheme}"
        stdscr.addstr(
            height // 2, (width - len(status_msg)) // 2, status_msg, curses.A_REVERSE
        )
        stdscr.refresh()
        curses.napms(500)  # Show message for 500ms

    def main(self, stdscr):
        curses.curs_set(0)
        self.setup_colors()
        stdscr.clear()

        while True:
            height, width = stdscr.getmaxyx()
            stdscr.bkgd(" ", curses.color_pair(4))
            stdscr.clear()

            UIComponents.draw_header(stdscr, self.current_view, self.task_manager)

            if self.current_view == "stats":
                UIComponents.draw_stats(stdscr, self.task_manager)
            else:
                UIComponents.draw_tasks(
                    stdscr,
                    self.task_manager.current_tasks,
                    self.selected_index,
                    self.current_view,
                    self.task_manager,
                )

            UIComponents.draw_footer(stdscr)
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord("q"):
                break
            elif key == ord("j") or key == curses.KEY_DOWN:
                self.selected_index = min(
                    self.selected_index + 1, len(self.task_manager.current_tasks) - 1
                )
            elif key == ord("k") or key == curses.KEY_UP:
                self.selected_index = max(self.selected_index - 1, 0)
            elif key == ord("v"):
                current_idx = self.views.index(self.current_view)
                self.current_view = self.views[(current_idx + 1) % len(self.views)]
            elif key == ord("a"):
                Dialogs.add_task(stdscr, self.task_manager)
            elif key == ord("e"):
                Dialogs.edit_task(stdscr, self.task_manager, self.selected_index)
            elif key == ord("?"):
                Dialogs.show_help(stdscr, self.config)
            elif key == ord("D") and self.task_manager.current_tasks:
                self.task_manager.delete_task(self.selected_index)
                self.selected_index = min(
                    self.selected_index, len(self.task_manager.current_tasks) - 1
                )
            elif key == ord("d") and self.task_manager.current_tasks:
                # Handle dependency creation
                depends_on_task = Dialogs.select_dependency(
                    stdscr, self.task_manager, self.selected_index
                )
                if depends_on_task:
                    self.task_manager.set_dependency(
                        self.selected_index, depends_on_task
                    )
            elif key == ord(" ") and self.task_manager.current_tasks:
                self.task_manager.complete_task(self.selected_index)
            elif key == ord("s"):
                self.change_color_scheme(stdscr)
            elif key == ord("T"):
                self.task_manager.toggle_completed()
                self.selected_index = min(
                    self.selected_index, len(self.task_manager.current_tasks) - 1
                )
            elif key == ord("p"):
                project = Dialogs.filter_by_project(stdscr, self.task_manager)
                if project is not None:
                    self.task_manager.filter_project = project
                    self.task_manager.update_task_lists()
            elif key == ord("t"):
                tag = Dialogs.filter_by_tag(stdscr, self.task_manager)
                if tag is not None:
                    self.task_manager.filter_tag = tag
                    self.task_manager.update_task_lists()
            elif key == ord("f"):
                filter_text = Dialogs.filter_tasks(stdscr)
                if filter_text is not None:
                    self.task_manager.set_filter(filter_text)
                    self.selected_index = 0  # Reset selection
            elif key == ord("c"):
                self.task_manager.clear_filters()
                self.selected_index = 0  # Reset selection


def main():
    app = TsakaroriTUI()
    curses.wrapper(app.main)


if __name__ == "__main__":
    main()
