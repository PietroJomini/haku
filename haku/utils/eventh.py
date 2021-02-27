from typing import Any, Callable
from haku.utils import call_safe


class Handler:
    """Basic event handler"""

    def _ensure_events(self):
        """Ensure the _events attr"""

        if not hasattr(self, '_events'):
            self._events = {}

    def on(self, tag: str, event: Callable):
        """Register an event"""

        self._ensure_events()
        self._events[tag] = event
        return self

    def dispatch(self, tag: str, *args, **argv) -> Any:
        """Dispatch an event"""

        self._ensure_events()
        cb = self._events[tag] if tag in self._events else None
        return call_safe(cb, *args, **argv)

    def _d(self, tag: str, *args, **argv):
        """Dispatch an event"""

        return self.dispatch(tag, *args, **argv)
