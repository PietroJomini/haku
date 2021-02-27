from typing import Callable, Any


def call_safe(cb: Callable, *args, **argv) -> Any:
    """Safely call a Callable"""

    try:
        cb(*args, **argv)
    except TypeError:
        return None


def abstract(method: Callable) -> Callable:
    """Marks a method as abstract"""

    def wrapper(*args, **kwargs):
        raise NotImplementedError(f'Missing required method {repr(method)}')
    return wrapper
