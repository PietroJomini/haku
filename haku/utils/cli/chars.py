from typing import List


class SpecialChars:
    """Special chars codes"""

    CURSOR_HIDE = "\x1b[?25l"
    CURSOR_SHOW = "\x1b[?25h"
    TEXT_BOLD = "\033[1m"
    TEXT_CLEAR = "\033[0m"


# https://unicode-search.net/unicode-namesearch.pl
class Box:
    """Box chars"""

    BARS: List[str] = ["│", "─"]
    CORNERS: List[str] = ["┐", "┌", "┘", "└"]
    TS: List[str] = ["┬", "┴", "├", "┤"]
    CROSS: str = "┼"
