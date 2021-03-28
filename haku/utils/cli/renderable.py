from typing import Callable, List, Optional, Tuple

from haku.utils import abstract


class Renderable:
    """Renderable item"""

    end: str = "\n"
    width: Optional[int] = None

    @staticmethod
    def from_function(w: Optional[int] = None):
        """Create a renderable from a function"""

        def decorator(cbk: Callable[[int], str]):
            """Internal decorator"""

            class R(Renderable):
                width = w

                def render(self, width: int) -> str:
                    return cbk(width=width)

            return R()

        return decorator

    @abstract
    def render(self, width: int) -> str:
        """Render the item"""


class Group(Renderable):
    """Renderable group"""

    def __init__(self, *items: Renderable, separator: str = "", flex: bool = True):
        self.items = items
        self.separator = separator
        self.flex = flex

        self.fw_items = [item for item in items if item.width is not None]
        self.uw_items = [item for item in items if item.width is None]
        self.fw = sum([item.width for item in self.fw_items])
        self.sw = len(separator) * (len(items) - 1)

    def apply_flex(
        self, items: List[Tuple[Renderable, int]], missing: int
    ) -> List[Tuple[Renderable, int]]:
        """Add missing width to items"""

        fixed_items = []

        augmented_items = 0
        for item, width in items:
            if item.width is None and augmented_items < missing:
                fixed_items.append((item, width + 1))
                augmented_items += 1
            else:
                fixed_items.append((item, width))

        return fixed_items

    def render(self, width: int):
        """Render the group"""

        rem = width - self.fw - self.sw
        uw = rem // len(self.uw_items) if len(self.uw_items) != 0 else 0

        items = [(i, uw if i.width is None else i.width) for i in self.items]

        if self.flex:
            missing_columns = width - sum([w for _, w in items]) - self.sw
            items = self.apply_flex(items, missing_columns)

        rendered = [item.render(width=width) for item, width in items]
        return self.separator.join(rendered)


class Line(Renderable):
    """Renderable line"""

    def __init__(self, pattern: str, width: Optional[int] = None):
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

    def __init__(self, text: str):
        self.text = text
        self.width = len(text)

    def render(self, width: int) -> str:
        """Render the text"""

        return self.text
