from numbers import Number
from threading import Thread
from time import sleep
from typing import Optional, Tuple

from haku.utils.cli import Console
from haku.utils.cli.renderable import Group, Line, Renderable, Text


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
        self.tot = tot
        self.position = 0

        self.description = Text(description) if description is not None else None

        self.bounds = bounds
        self.fill = fill
        self.void = void
        self.head = head

        @Renderable.from_function()
        def bar(width: int) -> str:
            return Group(
                Text(self.bounds[0]),
                Line(self.fill, int((width - 3) * self.percent)),
                Text(self.fill if self.completed else self.head),
                Line(self.void),
                Text(self.bounds[1]),
            ).render(width)

        self.bar = bar

    def to(self, position: int):
        """Set the bar to a position"""

        self.position = position
        self.console.print(self)

    @property
    def percent(self) -> float:
        """Get percentual progress"""

        return self.position / self.tot

    @property
    def completed(self) -> bool:
        """Check if the progress is completed"""

        return self.position == self.tot

    def render(self, width: int) -> str:
        """Render the bar"""

        items = [self.description, self.bar, Text(f"{int(self.percent*100):3g}%")]
        items = items[1:] if self.description is None else items
        return Group(*items, separator=" ").render(width)

    def __call__(self, delta: int):
        """Change the position by delta"""

        self.to(self.position + delta)

    def __enter__(self):
        self.console.hide_cursor()
        self.console.print(self)
        return self

    def __exit__(self, *_):
        self.console.show_cursor()


class Loader(Progress):
    """loader spinner"""

    end = "\r"

    def __init__(
        self,
        console: Console,
        description: Optional[str] = None,
        width: Optional[int] = None,
        bounds: Tuple[str, str] = ("[", "]"),
        slider: str = ">>>>>",
        void: str = "-",
        full: str = "=",
        delay: float = 0.05,
    ):
        self.console = console
        self.description = Text(description) if description is not None else None
        self.width = width

        self.runnign = False
        self.worker = None
        self.delay = delay

        self.bounds = bounds
        self.slider = slider
        self.void = void
        self.full = full

        self._innerbar = None

        @Renderable.from_function(width)
        def bar(width: int) -> str:
            return Group(
                Text(self.bounds[0]),
                Text(self.innerbar(width)) if self.runnign else Line(self.full),
                Text(self.bounds[1]),
            ).render(width)

        self.bar = bar

    def innerbar(self, width: int) -> str:
        """Update inner bar"""

        if self._innerbar is None:
            void_width = width - len(self.slider) - 2
            self._innerbar = self.slider + self.void * void_width

        self._innerbar = self._innerbar[-1] + self._innerbar[:-1]
        return self._innerbar

    def render(self, width: int) -> str:
        """Render the loader"""

        items = [self.description, self.bar]
        items = items[1:] if self.description is None else items
        return Group(*items, separator=" ").render(width)

    def __enter__(self):
        self.console.hide_cursor()
        self.runnign = True

        def worker():
            """Internal update worker"""

            while self.runnign:
                self.console.print(self)
                sleep(self.delay)

        self.worker = Thread(target=worker)
        self.worker.start()
        return self

    def __exit__(self, *_):
        self.runnign = False
        self.worker.join()

        self.console.print(self)
        self.console.show_cursor()
