# -*- coding: utf-8 -*-
"""
BehaveXContext — shared context object for before_all_workers / after_all_workers hooks.
"""

import json
from typing import NoReturn


class BehaveXContext:
    """Shared context passed to ``before_all_workers`` and ``after_all_workers`` hooks.

    Any attribute set on this object is automatically serialized and injected
    into the behave ``context`` in **every worker process** before ``before_all``
    runs, making the values available in all hooks and step definitions without
    any extra wiring.

    This lets you define configuration once in ``before_all_workers`` and read
    it from ``before_all``, ``before_scenario``, step definitions, etc., exactly
    as if you had set it there yourself.

    Example usage in ``environment.py``::

        import os

        def before_all_workers(context):
            context.base_url  = os.getenv("BASE_URL", "https://staging.example.com")
            context.api_key   = os.getenv("API_KEY")
            context.headless  = True
            context.retries   = 3

        def after_all_workers(context):
            # context still carries the values set in before_all_workers
            print(f"Teardown complete for env: {context.base_url}")

        def before_scenario(context, scenario):
            # Values injected transparently — no imports, no globals needed
            context.client = APIClient(context.base_url, context.api_key)

    Supported types
    ---------------
    Only JSON-serializable values can be shared across process boundaries:

    ==========  ========================================
    Supported   ``str``, ``int``, ``float``, ``bool``,
                ``list``, ``dict``, ``None``
    Unsupported database connections, file handles,
                locks, sockets, or any live object
    ==========  ========================================

    Attempting to set an unsupported type raises a :class:`TypeError` immediately
    with a descriptive message explaining what to do instead.

    Notes
    -----
    - Values are **copied** into each worker — mutations in one worker are not
      visible in other workers or in the main process.
    - To create live objects (e.g. a database connection), use the shared values
      as *configuration* in ``before_all`` or ``before_scenario`` to build them
      per worker.
    - ``before_all_workers`` runs in the **main BehaveX process**, before any
      worker is spawned. ``after_all_workers`` runs after all workers have
      finished, also in the main process.
    """

    def __setattr__(self, key: str, value: object) -> None:
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            raise TypeError(
                f"\n[BehaveX] Cannot set '{key}' in before_all_workers / after_all_workers.\n"
                f"  Value type '{type(value).__name__}' is not JSON-serializable and "
                f"cannot be shared with worker processes.\n"
                f"  Supported types: str, int, float, bool, list, dict, None.\n"
                f"  Tip: store the configuration needed to build the object here "
                f"(e.g. a URL or credentials string), then create the live object "
                f"per-worker inside before_all(context) or before_scenario(context, scenario)."
            )
        object.__setattr__(self, key, value)

    def __getattr__(self, key: str) -> NoReturn:
        raise AttributeError(
            f"[BehaveX] 'BehaveXContext' has no attribute '{key}'. "
            f"Make sure it was set in before_all_workers."
        )

    def _to_dict(self) -> dict:
        """Return all user-set attributes as a plain dict."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
