from typing import Optional, Union

from haku.utils.cli.chars import Box
from haku.utils.cli.renderable import Group, Line, Renderable, Text


class Table(Renderable):
    """Table renderable"""

    def __init__(self, box=Box):
        self.box = box
        self.rows = []

    def add_row(self, *row: Union[str, Renderable]):
        """Add a row of cells"""

        row = [
            cell if isinstance(cell, Renderable) else Text(cell, expand=True)
            for cell in row
        ]

        self.rows.append(row)

    def add_column(
        self,
        *column: Union[str, Renderable],
        same_width: bool = False,
        append: bool = False
    ):
        """Add a column of cells"""

        column = [
            cell if isinstance(cell, Renderable) else Text(cell, expand=True)
            for cell in column
        ]

        if same_width:

            # get max width from cells with fixed width
            max_width = max([cell.width or -1 for cell in column])

            if max_width > 0:
                # pre-render each element with the max width
                column = map(lambda cell: Group(cell, Line(" ")), column)
                column = map(lambda group: Text(group.render(max_width)), column)
                column = list(column)

        for i, cell in enumerate(column):

            # if needs to append, shift the index to the ne dof the list of rows
            i += len(self.rows) if append else 0
            self.add_row(cell) if i >= len(self.rows) else self.rows[i].append(cell)

    def hbound(self, over: Optional[str], below: Optional[str]) -> Group:
        """Create the horizontal separator for two rendered rows"""

        first = over is None
        last = below is None
        over = over or " " * len(below)
        below = below or " " * len(over)

        corners_map = {
            0: [self.box.TS[2], self.box.TS[3]],
            1: [self.box.CORNERS[1], self.box.CORNERS[0]],  # first row
            2: [self.box.CORNERS[3], self.box.CORNERS[2]],  # last row
        }

        pieces_map = {
            0: self.box.BARS[1],  # no bounds
            1: self.box.TS[1],  # over bound
            3: self.box.TS[0],  # under bound
            4: self.box.CROSS,  # over and under bound
        }

        corners = corners_map[1 * first + 2 * last]
        pieces = []

        for i in range(1, len(over) - 1):
            over_bound = i < len(over) and over[i] == self.box.BARS[0]
            below_bound = i < len(below) and below[i] == self.box.BARS[0]
            piece = pieces_map[1 * over_bound + 3 * below_bound]
            pieces.append(Text(piece))

        return Group(Text(corners[0]), *pieces, Text(corners[1]))

    def render(self, width: int) -> str:
        """Render the table"""

        rendered_rows = []
        for row in self.rows:

            # if all cells are with fixed width, expand last to fill the row
            if all([cell.width is not None for cell in row]):
                row[-1] = Group(row[-1], Line(" "))

            # pre-render the row
            group = Group(*row, separator=self.box.BARS[0], sandwich=True)
            rendered_rows.append(group.render(width))

        # rendered groups (rows and delimiters)
        groups = [self.hbound(None, rendered_rows[0]).render(width)]

        for i, row in enumerate(rendered_rows):
            groups.append(row)

            # render delimiter
            next_row = rendered_rows[i + 1] if i < len(rendered_rows) - 1 else None
            groups.append(self.hbound(row, next_row).render(width))

        return "\n".join(groups)

    def __add__(self, other):
        """Concatenate two tables"""

        t = Table(box=self.box)
        t.rows += self.rows
        t.rows += other.rows
        return t
