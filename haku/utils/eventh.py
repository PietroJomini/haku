from typing import Any, Callable, Dict, List, Optional

from haku.utils import call_safe


class Handler:
    """Event handler"""

    K_SEP: str = "."
    K_END: str = "end"

    def __init__(self):
        self.events: Dict[str, List[Callable]] = dict()

    def __init_subclass__(cls):
        cls.events: Dict[str, List[Callable]] = dict()

    def mkkey(self, key: str):
        """Ensure the presence of a key"""

        if key not in self.events:
            self.events[key] = []

    def on(self, key: str, event: Callable):
        """Register an event"""

        self.mkkey(key)
        self.events[key].append(event)

        return self

    def dispatch(self, key: str, *args: Any, **kwargs: Any):
        """Dispatch an event"""

        self.mkkey(key)
        for event in self.events[key]:
            call_safe(event, *args, **kwargs)

        return self

    def ping(self, key: str, cbk: Callable = print):
        """Ping an event"""

        return self.on(key, lambda *_: cbk(key))

    @classmethod
    def endkey(cls, key: str) -> str:
        """Compute end key"""

        return f"{key}{cls.K_SEP}{cls.K_END}"

    @classmethod
    def event(cls, key: str, endkey: Optional[str] = None):
        """Class decorator to create an event from a method"""

        endkey = endkey or cls.endkey(key)

        def decorator(cbk):
            """Internal decorator"""

            def wrapper(self: Handler, *args, **kwargs):
                """Actual wrapper"""

                self.dispatch(key, *args, **kwargs)
                res = cbk(self, *args, **kwargs)
                self.dispatch(endkey, *args, **kwargs)

                return res

            return wrapper

        return decorator

    @classmethod
    def async_event(cls, key: str, endkey: Optional[str] = None):
        """Class decorator to create an event from a method"""

        endkey = endkey or cls.endkey(key)

        def decorator(cbk):
            """Internal decorator"""

            async def wrapper(self: Handler, *args, **kwargs):
                """Actual wrapper"""

                self.dispatch(key, *args, **kwargs)
                res = await cbk(self, *args, **kwargs)
                self.dispatch(endkey, *args, **kwargs)

                return res

            return wrapper

        return decorator

    def listener(self, key: str):
        """Decorator to create a listener from a method"""

        def decorator(cbk):
            """Internal decorator"""

            self.on(key, cbk)

        return decorator
