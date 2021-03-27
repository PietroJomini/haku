from numbers import Number
from shutil import get_terminal_size
from sys import stdout
from typing import Any, Optional, TextIO, Tuple, Union

from haku.utils import abstract


class Cursor:
    """Cursor utils"""

    HIDE = "\x1b[?25l"
    SHOW = "\x1b[?25h"

    def __init__(self):
        self.hidden = False

    def hide(self):
        """Hide cursor"""

        self.hidden = True
        print(self.HIDE, end="\r")

    def show(self):
        """Show cursor"""

        self.hidden = False
        print(self.SHOW)


class Renderable:
    """Renderable item"""

    end = "\n"

    @abstract
    def render(self):
        """Render item"""


class Console:
    """Console utils"""

    def __init__(
        self,
        stdout: TextIO = stdout,
        columns: Optional[int] = None,
        lines: Optional[int] = None,
    ):
        self.stdout = stdout
        self.real_size = get_terminal_size()
        self.columns = columns or self.real_size.columns
        self.lines = lines or self.real_size.lines

        self.cursor = Cursor()

    @property
    def void_line(self):
        """Clear a line"""

        return " " * self.columns

    def print(self, item: Union[Any, Renderable], end: Optional[str] = None):
        """Render a renderable"""

        if isinstance(item, Renderable):
            print(item.render(), end=end or item.end)
        else:
            print(self.void_line, end="\r")
            print(item, end=end or "\n")


class Progress(Renderable):
    """Progress bar"""

    end = "\r"

    def __init__(
        self,
        console: Console,
        tot: Number,
        description: Optional[str] = None,
        bounds: Tuple[str, str] = ("[", "]"),
        fill: str = "=",
        void: str = " ",
        head: str = ">",
        fmt: str = "{description}{bar} {percent}",
    ):
        self.console = console
        self.description = f"{description} " if description is not None else ""
        self.tot = tot
        self.pos = 0

        self.bounds = bounds
        self.fill = fill
        self.void = void
        self.head = head
        self.fmt = fmt

    @property
    def width(self):
        """Get bar width"""

        partial = self.fmt.format(
            description=self.description,
            percent=self.percent_str,
            bar="",
        )
        return self.console.columns - len(partial)

    @property
    def percent(self):
        """Get progress in percentual"""

        return self.pos / self.tot

    @property
    def percent_str(self):
        """Get percent formatted string"""

        percent = int(self.percent * 100)
        return f"{percent:3g}%"

    @property
    def bar(self):
        """Get rendered bar"""

        width = self.width - 2

        head = self.head if self.tot != self.pos else self.fill
        filled = self.fill * int(width * self.percent - 1) + head
        void = self.void * (width - len(filled))

        return self.bounds[0] + filled + void + self.bounds[1]

    def advance(self, amount: Number):
        """Update the position of the bar"""

        self.to(self.pos + amount)

    def to(self, position: Number):
        """Set the bar to a specific position"""

        self.pos = position
        self.console.print(self)

    def render(self):
        """Render as a string"""

        return self.fmt.format(
            description=self.description,
            percent=self.percent_str,
            bar=self.bar,
        )

    def __enter__(self):
        self.console.cursor.hide()
        self.console.print(self)
        return self

    def __exit__(self, *_):
        self.console.cursor.show()
