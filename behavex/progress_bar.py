import sys
import time

from behavex.global_vars import global_vars


class ProgressBar:
    def __init__(self, prefix, total, bar_length=15, print_updates_in_new_lines=False):
        self.prefix = prefix
        self.total = total
        self.bar_length = bar_length
        self.current_iteration = 0
        self.start_time = global_vars.execution_start_time
        self.print_in_new_lines = print_updates_in_new_lines

    def start(self, start_increment=0):
        self.current_iteration = start_increment
        self._print_progress_bar(new_line=True)

    def update(self, increment=1):
        self.current_iteration += increment
        self._print_progress_bar()

    def finish(self, print_if_total_reached=False):
        if print_if_total_reached or self.current_iteration < self.total:
            self.current_iteration = self.total
            self._print_progress_bar(new_line=True)

    def _print_progress_bar(self, new_line=False):
        prefix = f"{self.prefix}: " if self.prefix else ""
        if self.total == 0:
            percent = 100
            filled_length = int(self.bar_length)
        else:
            percent = 100 * float(self.current_iteration / float(self.total))
            filled_length = int(self.bar_length * self.current_iteration // self.total)
        bar = '█' * filled_length + '-' * (self.bar_length - filled_length)
        elapsed_time = global_vars.execution_elapsed_time
        elapsed_formatted = time.strftime("%M:%S", time.gmtime(elapsed_time))
        progress_bar_content = f"\r{prefix}{percent:.0f}%|{bar}| {self.current_iteration}/{self.total} [{elapsed_formatted}]\r"
        if self.print_in_new_lines or new_line or percent == 100:
            print(progress_bar_content)
        else:
            sys.stdout.write(progress_bar_content)
            sys.stdout.flush()
