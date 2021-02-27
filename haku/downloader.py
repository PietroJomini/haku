from haku.meta import Chapter, Page
from haku.utils import eventh
from typing import List
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

    async def __page(self, session: aiohttp.ClientSession, page: Page) -> Page:
        """Internal passthrought to `self._page`"""

        self._d('page', page)
        return await self._page(session, page)

    async def page(self, page: Page) -> Page:
        """Download a page"""

        async with aiohttp.ClientSession() as session:
            return await self.__page(session, page)

    def page_sync(self, page: Page) -> Page:
        """Download a page"""

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.page(page))

    async def _chapter(self, session: aiohttp.ClientSession, chapter: Chapter) -> Chapter:
        """Chapter async worker"""

        nc = copy(chapter)
        self.dispatch('chapter', nc)

        nc._pages = await asyncio.gather(*(
            asyncio.ensure_future(self.__page(session, page))
            for page in nc._pages
        ))

        return nc

    async def chapter(self, chapter: Chapter) -> Chapter:
        """Download a chapter"""

        async with aiohttp.ClientSession() as session:
            return await self._chapter(session, chapter)

    def chapter_sync(self, chapter: Chapter) -> Chapter:
        """Download a chapter"""

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.chapter(chapter))

    async def chapters(self, *chapters: List[Chapter]) -> List[Chapter]:
        """Download a set of chapters"""

        async with aiohttp.ClientSession() as session:
            return await asyncio.gather(*(
                asyncio.ensure_future(self._chapter(session, chapter))
                for chapter in chapters
            ))

    def chapters_sync(self, *chapters: List[Chapter]) -> List[Chapter]:
        """Download a set of chapters"""

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.chapters(*chapters))
