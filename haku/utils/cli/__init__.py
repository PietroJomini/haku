from shutil import get_terminal_size
from sys import stdout
from typing import Any, Optional, TextIO, Union

from .chars import SpecialChars
from .renderable import Renderable, Text


class Console:
    """Console wrapper"""

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

        self.columns = min(self.columns, self.real_size.columns)
        self.lines = min(self.lines, self.real_size.lines)

        self.cursor_hidden = False

    def hide_cursor(self):
        """Hide the cursor"""

        self.cursor_hidden = False
        self.print(SpecialChars.CURSOR_HIDE, end="\r")

    def show_cursor(self):
        """Show the cursor"""

        self.cursor_hidden = True
        self.print(SpecialChars.CURSOR_SHOW)

    def print(self, item: Union[Any, Renderable], end: Optional[str] = None):
        """Render an item"""

        item = item if isinstance(item, Renderable) else Text(str(item))
        print(item.render(self.columns), end=end or item.end or "\n")
