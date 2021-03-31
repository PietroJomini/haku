from enum import Enum
from typing import Callable, List, Optional, Tuple

from haku.utils import abstract
from haku.utils.cli.chars import SpecialChars


class Flex(Enum):
    """Flex directives"""

    grow = 0
    fixed = 1


class Renderable:
    """Renderable item"""

    end: str = "\n"
    width: Optional[int] = None
    flex: Flex = Flex.fixed

    @staticmethod
    def from_function(w: Optional[int] = None):
        """Create a renderable from a function"""

        def decorator(cbk: Callable[[int], str]):
            """Internal decorator"""

            class R(Renderable):
                def render(self, width: int) -> str:
                    return cbk(width)

            R.width = w
            R.flex = Flex.fixed if w is not None else Flex.grow
            return R()

        return decorator

    @abstract
    def render(self, width: int) -> str:
        """Render the item"""


class Dummy(Renderable):
    """Dummy renderable"""

    width = 0

    @staticmethod
    def render(width: int) -> str:
        """Render nothing"""

        return ""


class Group(Renderable):
    """Renderable group"""

    def __init__(
        self,
        *items: Renderable,
        separator: str = "",
        sandwich: bool = False,
        width: Optional[int] = None,
        fix_flex: bool = True,
    ):
        self.items = items
        self.separator = separator
        self.width = width
        self.sandwich = sandwich
        self.fix_flex = fix_flex

        if self.sandwich:
            self.items = [Dummy, *self.items, Dummy]

    def flex(self, width: int) -> List[Tuple[Renderable, int]]:
        """Add missing width to items"""

        fixed_items = [item for item in self.items if item.flex == Flex.fixed]
        grow_items = [item for item in self.items if item.flex == Flex.grow]

        fix_width = sum([item.width for item in fixed_items])
        sep_width = len(self.separator) * (len(self.items) - 1)
        rem_width = width - fix_width - sep_width

        # calcualte the width of each item marked as growable
        growth = rem_width // len(grow_items) if len(grow_items) > 0 else 0

        # if "holes" remains due to the "low resolution" of the console,
        # repeatly apply fixtures until the holes are (mostly) evenly filled
        # between the items marked as Flex.grow
        diff = rem_width % len(grow_items) if len(grow_items) > 0 else 0
        fixtures = [0 for _ in self.items]

        if diff > 0 and self.fix_flex:
            for i in range(diff):
                fixtures[i % len(fixtures)] += 1

        fixtures = iter(fixtures)
        items = [
            (item, item.width if item.flex == Flex.fixed else growth + next(fixtures))
            for item in self.items
        ]

        return items

    def render(self, width: int):
        """Render the group"""

        items = self.flex(width)
        rendered = [item.render(width) for item, width in items]
        return self.separator.join(rendered)


class Line(Renderable):
    """Renderable line"""

    def __init__(self, pattern: str, width: Optional[int] = None):
        self.flex = Flex.grow if width is None else Flex.fixed
        self.pattern = pattern
        self.width = width

    def render(self, width: int) -> str:
        """Render the line"""

        width = self.width or width
        reps = width // len(self.pattern) + 1
        line = self.pattern * reps
        return line[:width]


class Text(Renderable):
    """Renderable text"""

    def __init__(
        self,
        text: str,
        expand: bool = False,
        clip: bool = True,
        center: bool = False,
        bold: bool = False,
    ):
        self.text = text
        self.expand = expand
        self.clip = clip
        self.center = center
        self.bold = bold

        self.width = len(text) if not expand else None
        self.flex = Flex.fixed if not expand else Flex.grow

    def render(self, width: int) -> str:
        """Render the text"""

        if self.clip and len(self.text) > width:
            self.text = self.text[: width - 3] + "..."

        if self.expand:
            items = [Line(" "), Text(self.text, bold=self.bold), Line(" ")]
            return Group(*(items if self.center else items[1:])).render(width)

        if self.bold:
            self.text = f"{SpecialChars.TEXT_BOLD}{self.text}{SpecialChars.TEXT_CLEAR}"

        return self.text
