from numbers import Number
from typing import Callable

from haku.meta import Chapter, Manga


class Filter:
    """Filters, to be applied to a Shelf instance"""

    @staticmethod
    def title_in(*titles: str):
        """Filter chapters if title in *titles"""

        return Filter(lambda chapter: chapter.title in titles)

    @staticmethod
    def index_in(*index: Number):
        """Filter chapters if index in *index"""

        return Filter(lambda chapter: chapter.index in index)

    @staticmethod
    def index_range(start: Number, end: Number):
        """Filter chapters if index in [start, end]"""

        return Filter(lambda chapter: start <= chapter.index <= end)

    @staticmethod
    def has_volume():
        """Filter chapters if volume is not None"""

        return Filter(lambda chapter: chapter.volume is not None)

    @staticmethod
    def volume_in(*volumes: Number):
        """Filter chapters if volume in *volumes"""

        f = Filter(lambda chapter: chapter.volume in volumes)
        return Filter.has_volume() & f

    @staticmethod
    def volume_range(start: Number, end: Number):
        """Filter chapters if volue in [start, end]"""

        f = Filter(lambda chapter: start <= chapter.volume <= end)
        return Filter.has_volume() & f

    def __init__(self, f: Callable[[Chapter], bool]):
        self.f = f

    def __and__(self, other):
        return Filter(lambda chapter: self.f(chapter) and other.f(chapter))

    def __or__(self, other):
        return Filter(lambda chapter: self.f(chapter) or other.f(chapter))

    def __invert__(self):
        return Filter(lambda chapter: not self.f(chapter))

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


class Shelf:
    """Manga shelf"""

    def __init__(self, manga: Manga):
        self.manga = manga

    def filter(self, f: Filter):
        """Apply a filter"""

        self.manga.chapters = list(filter(f.f, self.manga.chapters))
