from typing import List, Optional, Type
from haku.meta import Chapter, Page
from haku.fs import write_page
from haku.utils import eventh
from pathlib import Path
from PIL import Image
from copy import copy
import aiohttp
import asyncio
import io


class Downloader(eventh.Handler):
    """Downloader defaults"""

    async def _page(self, session: aiohttp.ClientSession, page: Page) -> Page:
        """Page async worker"""

        np = copy(page)
        async with session.get(np.url) as response:
            raw = await response.read()
            stream = io.BytesIO(raw)
            np._raw = Image.open(stream)
            return np

    async def __page(self, session: aiohttp.ClientSession, page: Page, path: Path):
        """Download and write pages to disk"""

        self._d('page', page)
        np = await self._page(session, page)

        self._d('page.write', np)
        write_page(np, path)

        page._raw.close()
        del page._raw

    async def page(self, page: Page, path: Path):
        """Download a page"""

        async with aiohttp.ClientSession() as session:
            await self.__page(session, page, path=path)

    def page_sync(self, page: Page, path: Path):
        """Download a page"""

        asyncio.run(self.page(page, path=path))

    async def _chapter(self, session: aiohttp.ClientSession, chapter: Chapter, path: Path):
        """Chapter async worker"""

        self.dispatch('chapter', chapter)
        await asyncio.gather(*(
            asyncio.ensure_future(self.__page(
                session, page, path / chapter.title))
            for page in chapter._pages
        ))

    async def chapter(self, chapter: Chapter, path: Path = Path.cwd()):
        """Download a chapter"""

        async with aiohttp.ClientSession() as session:
            await self._chapter(session, chapter, path=path)

    def chapter_sync(self, chapter: Chapter, path: Path = Path.cwd()):
        """Download a chapter"""

        asyncio.run(self.chapter(chapter, path=path))

    async def chapters(self, *chapters: List[Chapter], path: Path = Path.cwd()):
        """Download a set of chapters"""

        async with aiohttp.ClientSession() as session:
            await asyncio.gather(*(
                asyncio.ensure_future(self._chapter(
                    session, chapter, path=path))
                for chapter in chapters
            ))

    def chapters_sync(self, *chapters: List[Chapter], path: Path = Path.cwd()):
        """Download a set of chapters"""

        asyncio.run(self.chapters(*chapters, path=path))
