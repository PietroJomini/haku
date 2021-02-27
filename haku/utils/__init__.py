from typing import Callable


def abstract(method: Callable) -> Callable:
    """Marks a method as abstract"""

    def wrapper(*args, **kwargs):
        raise NotImplementedError(f'Missing required method {repr(method)}')
    return wrapper
