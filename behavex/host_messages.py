# -*- coding: utf-8 -*-

import io
import signal
import sys
import threading

from behavex.run_state import state

_main_thread_putting_to_host_queue = False
_ctrl_c_deferred_until_put_ends = False


def stop_behave_on_first_ctrl_c(signum, frame):
    global _ctrl_c_deferred_until_put_ends
    # A terminal's Ctrl+C reaches the worker twice: from the console and from the host
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    if _main_thread_putting_to_host_queue:
        _ctrl_c_deferred_until_put_ends = True
        return
    raise KeyboardInterrupt


class HostQueueDeferringCtrlC:
    """Raises a Ctrl+C that reaches the worker mid-put only once the put completes."""

    def __init__(self, host_queue):
        self._host_queue = host_queue

    def put(self, message):
        # A KeyboardInterrupt raised mid-put leaves the manager connection out of sync, so the next put fails
        global _main_thread_putting_to_host_queue, _ctrl_c_deferred_until_put_ends
        if threading.current_thread() is not threading.main_thread():
            self._host_queue.put(message)
            return
        _main_thread_putting_to_host_queue = True
        try:
            self._host_queue.put(message)
        finally:
            _main_thread_putting_to_host_queue = False
            ctrl_c_deferred, _ctrl_c_deferred_until_put_ends = _ctrl_c_deferred_until_put_ends, False
        if ctrl_c_deferred:
            raise KeyboardInterrupt


def forward_worker_messages(host_queue):
    for message_kind, payload in iter(host_queue.get, None):
        if message_kind == 'output':
            # The host may have redirected sys.stdout, as an MCP stdio server does
            sys.stdout.write(payload)
            sys.stdout.flush()
        elif message_kind == 'progress':
            scenario_key, progress_fields = payload
            state.report_scenario_progress(scenario_key, **progress_fields)


class StdoutToHostQueue(io.TextIOBase):
    """Sends each complete line written to it to the host process through host_queue."""
    encoding = 'utf-8'

    def __init__(self, host_queue, original_stdout):
        super().__init__()
        self._host_queue = host_queue
        self._original_stdout = original_stdout
        self._pending_text = ''

    def writable(self):
        return True

    def fileno(self):
        # Output written to the descriptor, such as a subprocess's, bypasses the host as in parallel runs
        return self._original_stdout.fileno()

    def write(self, text):
        self._pending_text += text
        if '\n' in text:
            complete_lines, _, self._pending_text = self._pending_text.rpartition('\n')
            self._host_queue.put(('output', complete_lines + '\n'))
        return len(text)

    def flush(self):
        if self._pending_text:
            pending_text, self._pending_text = self._pending_text, ''
            self._host_queue.put(('output', pending_text))
