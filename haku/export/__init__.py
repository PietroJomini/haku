import asyncio
from multiprocessing import Manager, Pool
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

from PIL import Image

from haku.meta import Chapter, Manga, Page
from haku.raw.fs import FTree, Reader
from haku.shelf import Shelf
from haku.utils import abstract, eventh


class Merge:
    """Merge methods"""

    MergeCallable = Callable[
        [List[Tuple[Chapter, Any]], Manga], List[Tuple[List[Tuple[Chapter, Any]], Path]]
    ]

    @staticmethod
    def volume() -> MergeCallable:
        """Split chapters in volumes"""

        def method(chapters, manga):

            volumes = {chapter.volume: [] for chapter, _ in chapters}
            for chapter, data in chapters:
                volumes[chapter.volume].append((chapter, data))

            return [(volumes[volume], f"{volume:g}") for volume in volumes]

        return method

    @staticmethod
    def manga() -> MergeCallable:
        """Split chapters in volumes"""

        def method(chapters, manga):
            return [(chapters, manga.title)]

        return method


class Converter(eventh.Handler):
    """Convert manga"""

    def __init__(
        self,
        manga: Union[Manga, Shelf],
        reader: Union[Reader, FTree],
        out: Union[FTree, Path],
    ):
        self.manga = manga if isinstance(manga, Manga) else manga.manga
        self.out = out if isinstance(out, FTree) else FTree(out, self.manga)
        self.reader = reader if isinstance(reader, Reader) else Reader(reader)

    def convert(self, processes: Optional[int] = None):
        """Convert a manga"""

        self._prepare()

        manager = Manager()
        self.merge_data = manager.list()

        with Pool(processes=processes) as pool:
            pool.map(self.conver_chapter, self.manga.chapters)

        self._followup()

    def conver_chapter(self, chapter: Chapter) -> bool:
        """Convert a chapter"""

        self.dispatch("chapter", chapter)
        images = asyncio.run(self.reader.chapter(chapter))
        images.sort(key=lambda image: image[0].index)

        should_cleanup, chapter = self._convert_chapter(chapter, images)
        self.merge_data.append(chapter)

        if should_cleanup:
            for page, image in images:
                image.close()

        self.dispatch(self.endkey("chapter"), chapter)

    def merge(self, method: Merge.MergeCallable, dest: Path):
        """Merge chapters"""

        if not hasattr(self, "merge_data"):
            return

        dest = dest if isinstance(dest, FTree) else FTree(dest, self.manga)
        for chunk, name in method(self.merge_data, self.manga):
            self._merge(chunk, dest.root, name)

    @abstract
    def _convert_chapter(
        self, chapter: Chapter, pages: List[Tuple[Page, Image.Image]]
    ) -> Tuple[bool, Tuple[Chapter, Any]]:
        """Convert a chapter"""

    def _followup(self):
        """Executed after all the chapters have been converted"""

    def _prepare(self):
        """Prepare to convert"""

        self.out.root.mkdir(parents=True, exist_ok=True)

    @abstract
    def _merge(self, chapters: List[Tuple[Chapter, Any]], out: Path, name: str):
        """Merge a series of chapters"""
