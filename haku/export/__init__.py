import asyncio
from multiprocessing import Manager, Pool
from pathlib import Path
from typing import List, Optional, Tuple, Union

from PIL import Image

from haku.meta import Chapter, Manga, Page
from haku.raw.fs import FTree, Reader
from haku.shelf import Shelf
from haku.utils import abstract, eventh


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
        self.shared_list = manager.list()
        self.shared_dict = manager.dict()

        with Pool(processes=processes) as pool:
            pool.map(self.conver_chapter, self.manga.chapters)

        self._followup()

    def conver_chapter(self, chapter: Chapter) -> bool:
        """Convert a chapter"""

        self.dispatch("chapter", chapter)
        images = asyncio.run(self.reader.chapter(chapter))
        images.sort(key=lambda image: image[0].index)

        should_cleanup = self._convert_chapter(chapter, images)
        if should_cleanup:
            for page, image in images:
                image.close()

        self.dispatch(self.endkey("chapter"), chapter)

    @abstract
    def _convert_chapter(self, chapter: Chapter, pages: List[Tuple[Page, Image.Image]]):
        """Convert a chapter"""

    @abstract
    def _followup(self):
        """Executed after all the chapters have been converted"""

    def _prepare(self):
        """Prepare to convert"""

        self.out.root.mkdir(parents=True, exist_ok=True)
