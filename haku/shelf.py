from typing import Callable

from haku.meta import Chapter, Manga


class Filter:
    """Filters, to be applied to a Shelf instance"""

    @staticmethod
    def chapter_index(*index: str):
        """Filter chapters based on a set of index"""

        return Filter(lambda chapter: chapter.index in index)

    @staticmethod
    def chapter_title(*titles: str):
        """Filter chapters based on a set of index"""

        return Filter(lambda chapter: chapter.title in titles)

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
