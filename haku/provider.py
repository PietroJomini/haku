from haku.meta import Chapter, Page, Manga
from aiohttp.client import ClientSession
from haku.utils import abstract, eventh
from typing import List, Optional, Type
from haku.downloader import Downloader
from bs4 import BeautifulSoup
from PIL import Image
import aiohttp
import asyncio


class Helpers():
    """Provider helpers"""

    @staticmethod
    async def scrape_webpage(session: aiohttp.ClientSession, url: str) -> BeautifulSoup:
        """Scrape a webpage into a BeautifulSoup soup"""

        async with session.get(url) as response:
            content = await response.text()
            return BeautifulSoup(content, 'html.parser')


class Provider(eventh.Handler):
    """Provider default"""

    name: str
    pattern: str

    enabled: bool = True
    downloader: Type[Downloader] = Downloader

    def __init__(self, url: str):
        self.url = url

    def fetch_sync(self) -> Manga:
        """Fetch chapters"""

        return asyncio.run(self.fetch())

    async def fetch(self) -> Manga:
        """Fetch chapters"""

        async with aiohttp.ClientSession() as session:

            self._d('fetch.title')
            title = await self.fetch_title(self.url, session)

            self._d('fetch.cover')
            cover = await self.fetch_cover(self.url, session)

            manga = Manga(title=title, url=self.url, cover=cover)

            self._d('fetch.chapters')
            chapters_meta = await self.fetch_chapters(self.url, session)

            self._d('fetch.pages')
            pages = await asyncio.gather(*(
                asyncio.ensure_future(self.fetch_pages(chapter, session))
                for chapter in chapters_meta
            ))

            manga.chapters = [
                Chapter(url=c.url, index=c.index, title=c.title,
                        volume=c.volume, _pages=p)
                for c, p in zip(chapters_meta, pages)
            ]

            return manga

    @abstract
    async def fetch_chapters(self, url: str, session: aiohttp.ClientSession) -> List[Chapter]:
        """Retrieve chapters list"""

    @abstract
    async def fetch_pages(self, chapter: Chapter, session: aiohttp.ClientSession) -> List[Page]:
        """Retrieve chapter pages"""

    @abstract
    async def fetch_title(self, url: str, session: aiohttp.ClientSession) -> str:
        """Retrieve manga title"""

    async def fetch_cover(self, url: str, session: aiohttp.ClientSession) -> Optional[Type[Image.Image]]:
        """Retrieve manga cover"""

        return None
