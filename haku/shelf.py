import re
from functools import reduce
from numbers import Number
from typing import Callable, Dict, List, Optional, Tuple

from haku.meta import Chapter, Manga


class Filter:
    """Filters, to be applied to a Shelf instance"""

    @staticmethod
    def stringified(src: str):
        """Parse stringified filter"""

        return StringifiedFilter.parse(src)

    @staticmethod
    def true():
        """Filter all chapters"""

        return Filter(
            lambda chapter: True,
            "True",
        )

    @staticmethod
    def false():
        """Filter no chapters"""

        return Filter(
            lambda chapter: False,
            "False",
        )

    @staticmethod
    def title_in(*titles: str):
        """Filter chapters if title in *titles"""

        return Filter(
            lambda chapter: chapter.title in titles,
            f"title in ({', '.join(titles)})",
        )

    @staticmethod
    def index_in(*index: Number):
        """Filter chapters if index in *index"""

        return Filter(
            lambda chapter: chapter.index in index,
            f"index in ({', '.join(map(str, index))})",
        )

    @staticmethod
    def index_range(start: Number, end: Number):
        """Filter chapters if index in [start, end]"""

        return Filter(
            lambda chapter: start <= chapter.index <= end,
            f"{start} <= index <= {end}",
        )

    @staticmethod
    def has_volume():
        """Filter chapters if volume is not None"""

        return Filter(
            lambda chapter: chapter.volume is not None,
            "volume != None",
        )

    @staticmethod
    def volume_in(*volumes: Number):
        """Filter chapters if volume in *volumes"""

        return Filter.has_volume() & Filter(
            lambda chapter: chapter.volume in volumes,
            f"volume in ({', '.join(map(str, volumes))})",
        )

    @staticmethod
    def volume_range(start: Number, end: Number):
        """Filter chapters if volue in [start, end]"""

        return Filter.has_volume() & Filter(
            lambda chapter: start <= chapter.volume <= end,
            f"{start} <= volume <= {end}",
        )

    def __init__(self, f: Callable[[Chapter], bool], repr: Optional[str] = None):
        self.repr = repr
        self.f = f

    def __and__(self, other):
        return Filter(
            lambda chapter: self.f(chapter) and other.f(chapter),
            f"({self.repr}) & ({other.repr})",
        )

    def __or__(self, other):
        return Filter(
            lambda chapter: self.f(chapter) or other.f(chapter),
            f"({self.repr}) | ({other.repr})",
        )

    def __invert__(self):
        return Filter(
            lambda chapter: not self.f(chapter),
            f"!({self.repr})",
        )

    @staticmethod
    def _and(a, b):
        """Filter if a and b"""

        return a & b

    @staticmethod
    def _or(a, b):
        """Filter if a or b"""

        return a | b

    @staticmethod
    def _not(f):
        """Filter if not f"""

        return ~f

    def __repr__(self):
        """Filter repr"""

        return f"Filter[{self.repr}]" if self.repr is not None else super().__repr__()


class StringifiedFilter:
    """Stringified filters parser

    + `<Number>a:<Number>b` `Filter.index_range(a, b)`
    + `<Number>a` `Filter.index_in(a, b)`
    + `<Text>a` `Filter.title_in(a)`
    + `V[F]` `Filter.volume_*(*)`
    """

    sep: str = " "
    v_re: str = r"V\[(.*?)\]"
    in_re: str = r"^([.\d]+)$"
    title_re: str = r"^(\w+)$"
    range_re = r"^([.\d]+):([.\d]+)$"

    @classmethod
    def _split_tokens(cls, f: str) -> List[str]:
        """Split tokens"""

        return [f.strip() for f in f.split(cls.sep) if f != ""]

    @classmethod
    def _tokenize(
        cls, to_tokenize: str
    ) -> Tuple[List[Tuple[Number, Number]], List[Number], List[str]]:
        """Tokenize"""

        ranges = []
        index_in = []
        title_in = []

        for token in cls._split_tokens(to_tokenize):
            if re.match(cls.range_re, token):
                groups = re.search(cls.range_re, token)
                start = float(groups.group(1))
                end = float(groups.group(2))
                ranges.append((start, end))

            elif re.match(cls.in_re, token):
                groups = re.search(cls.in_re, token)
                index_in.append(float(groups.group(1)))

            elif re.match(cls.title_re, token):
                groups = re.search(cls.title_re, token)
                a = groups.group(1)
                title_in.append(a)

        return ranges, index_in, title_in

    @classmethod
    def parse(cls, f: str) -> Filter:
        """Parse stringified filter"""

        # separate index filters from volume and filters
        v_filters = re.findall(cls.v_re, f)
        filters = re.sub(cls.v_re, "", f)

        # tokenize filters
        parsed_tokens = cls._tokenize(filters)
        parsed_v_tokens = cls._tokenize(" ".join(v_filters))

        # transform tokens into filters
        ranges = (Filter.index_range(a, b) for a, b in parsed_tokens[0])
        v_ranges = (Filter.volume_range(a, b) for a, b in parsed_v_tokens[0])
        index_in = Filter.index_in(*parsed_tokens[1])
        volume_in = Filter.volume_in(*parsed_v_tokens[1])
        title_in = Filter.title_in(*parsed_tokens[2], *parsed_v_tokens[2])

        # join filters
        return reduce(
            lambda a, b: a | b,
            [*ranges, *v_ranges, index_in, title_in, volume_in],
        )


class Shelf:
    """Manga shelf"""

    def __init__(self, manga: Manga):
        self.manga = manga

    def filter(self, f: Filter):
        """Apply a filter"""

        self.manga.chapters = list(filter(f.f, self.manga.chapters))
        return self

    def sort(self):
        """Sort chapters"""

        self.manga.chapters.sort(key=lambda chapter: (chapter.index, chapter.volume))
        return self

    def split_volumes(self) -> Dict[Number, List[Chapter]]:
        """Split manga into volumes"""

        volumes = {chapter.volume: [] for chapter in self.manga.chapters}

        for chapter in self.manga.chapters:
            volumes[chapter.volume].append(chapter)

        return volumes
