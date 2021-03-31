from typing import List, Optional, Type

from haku.utils.cli.renderable import Group, Line, Renderable, Text


# https://unicode-search.net/unicode-namesearch.pl
class Box:
    """Box chars"""

    bars: List[Text] = [Text("│"), Text("─")]
    corners: List[Text] = [Text("┐"), Text("┌"), Text("┘"), Text("└")]
    ts: List[Text] = [Text("┬"), Text("┴"), Text("├"), Text("┤")]
    cross: Text = Text("┼")


class Table(Renderable):
    """Table renderable"""

    def __init__(self, box: Type[Box] = Box):
        self.rows = []
        self.box = box

    def add_row(self, row: List[str]):
        """Add a row of cells"""

        self.rows += [row]

    def delimiter(
        self,
        width: int,
        row: Optional[str] = None,
        next_row: Optional[str] = None,
    ) -> str:
        """Create the horizontal delimiter for a row"""

        if row is None:
            corners = [self.box.corners[1], self.box.corners[0]]
        elif next_row is None:
            corners = [self.box.corners[3], self.box.corners[2]]
        else:
            corners = [self.box.ts[2], self.box.ts[3]]

        row = row or Line(" ").render(width)
        next_row = next_row or Line(" ").render(width)

        pieces = []
        pieces_map = {
            1: self.box.ts[1],
            3: self.box.ts[0],
            4: self.box.cross,
            0: self.box.bars[1],
        }

        for i in range(1, width - 1):
            up = 1 * (row[i] == self.box.bars[0].text)
            down = 3 * (next_row[i] == self.box.bars[0].text)
            pieces.append(pieces_map[up + down])

        return Group(corners[0], *pieces, corners[1]).render(width)

    def render(self, width: int) -> str:
        """Render the tables"""

        rows = [
            Group(
                Text(""),
                *[Text(el, expand=True) for el in row],
                Text(""),
                separator=self.box.bars[0].text,
            ).render(width)
            for row in self.rows
        ]

        groups = [self.delimiter(width, None, rows[0])]
        for i, row in enumerate(rows):
            groups.append(rows[i])
            next_row = rows[i + 1] if i < len(rows) - 1 else None
            groups.append(self.delimiter(width, rows[i], next_row))

        return "\n".join(groups)
