from numbers import Number
from shutil import get_terminal_size
from sys import stdout
from threading import Thread
from time import sleep
from typing import Any, Callable, Optional, TextIO, Tuple, Union

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
    width: Optional[int] = None

    @staticmethod
    def from_function(cbk: Callable):
        """Create a renderable from a function"""

        class R(Renderable):
            def render(self, width: int):
                return cbk(width)

        return R()

    @abstract
    def render(self, width: int):
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
            print(item.render(self.columns), end=end or item.end)
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
    ):
        self.console = console
        self.description = Text(description) if description is not None else None
        self.tot = tot
        self.pos = 0

        self.bounds = bounds
        self.fill = fill
        self.void = void
        self.head = head

    @property
    def percent(self) -> float:
        """Get progress in percentual"""

        return self.pos / self.tot

    @property
    def completed(self) -> bool:
        """check if the progress is completed"""

        return self.pos == self.tot

    def bar(self):
        """Build inner bar as a Group"""

        @Renderable.from_function
        def render(width: int):
            return Group(
                Text(self.bounds[0]),
                Line(fill=self.fill, width=int((width - 3) * self.percent)),
                Text(self.fill if self.completed else self.head),
                Line(fill=self.void),
                Text(self.bounds[1]),
            ).render(width)

        return render

    def advance(self, amount: Number):
        """Update the position of the bar"""

        self.to(self.pos + amount)

    def to(self, position: Number):
        """Set the bar to a specific position"""

        self.pos = position
        self.console.print(self)

    def render(self, width: int):
        """Render as a string"""

        items = [self.description, self.bar(), Text(f"{int(self.percent*100):3g}%")]
        items = items[1:] if self.description is None else items
        group = Group(*items, separator=" ")
        return group.render(width)

    def __enter__(self):
        self.console.cursor.hide()
        self.console.print(self)
        return self

    def __exit__(self, *_):
        self.console.cursor.show()


class Loader(Renderable):
    """Loader bar"""

    end = "\r"

    def __init__(
        self,
        console: Console,
        description: Optional[str] = None,
        bounds: Tuple[str, str] = ("[", "]"),
        slider: str = ">>>>>",
        void: str = "-",
        full: str = "=",
        fmt: str = "{description}{bar}",
        delay: float = 0.05,
    ):
        self.console = console
        self.description = f"{description} " if description is not None else ""

        self.running = False
        self.worker = None
        self.delay = delay

        self.bounds = bounds
        self.slider = slider
        self.void = void
        self.full = full
        self.fmt = fmt

        self.inner_bar = self.slider + self.void * (self.width - 2 - len(self.slider))

    @property
    def width(self):
        """Get bar width"""

        partial = self.fmt.format(description=self.description, bar="")
        return self.console.columns - len(partial)

    @property
    def bar(self):
        """Get rendered bar"""

        return self.bounds[0] + self.inner_bar + self.bounds[1]

    def update(self):
        """Update the slider position"""

        self.inner_bar = self.inner_bar[-1] + self.inner_bar[:-1]

    def update_worker(self):
        """Update the slider repeatedly"""

        while self.running:
            self.update()
            self.console.print(self)
            sleep(self.delay)

    def fill(self):
        """Fill the bar"""

        self.inner_bar = self.full * (self.width - 2)

    def render(self, _):
        """Render as a string"""

        return self.fmt.format(
            description=self.description,
            bar=self.bar,
        )

    def __enter__(self):
        self.console.cursor.hide()
        self.running = True
        self.worker = Thread(target=self.update_worker)
        self.worker.start()
        return self

    def __exit__(self, *_):
        self.running = False
        self.worker.join()

        self.fill()
        self.console.print(self)
        self.console.cursor.show()


class Text(Renderable):
    """Text renderable"""

    def __init__(self, text: str):
        self.text = text
        self.width = len(text)

    def render(self, _):
        """Render the text"""

        return self.text


class Line(Renderable):
    """Line renderable"""

    def __init__(self, fill: str = "-", width: Optional[int] = None):
        self.fill = fill
        self.width = width

    def render(self, width: int):
        """Render a line"""

        return self.fill * width


class Group(Renderable):
    """Group of renderables"""

    def __init__(self, *items: Union[str, Renderable], separator: str = ""):
        self.items = items
        self.separator = separator

        self.separators_len = len(separator) * (len(items) - 1)
        self.fixed_width = sum([item.width for item in items if item.width is not None])
        self.uw_items = [i for i in self.items if i.width is None]

    def render(self, width: int):
        """Render the group"""

        rem_width = width - self.fixed_width - self.separators_len
        uw_items_width = (
            rem_width // len(self.uw_items) if len(self.uw_items) != 0 else 0
        )

        rendered = [
            item.render(uw_items_width if item.width is None else item.width)
            for item in self.items
        ]

        return self.separator.join(rendered)
