from aiohttp.client import ClientSession
from haku.utils import abstract, eventh
from haku.downloader import Downloader
from haku.meta import Chapter, Page
from bs4 import BeautifulSoup
from typing import List
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
    downloader: Downloader = Downloader

    def __init__(self, url: str):
        self.url = url

    def fetch_sync(self):
        """Fetch chapters"""

        loop = asyncio.get_event_loop()
        chapters = loop.run_until_complete(self.fetch())

        return chapters

    async def fetch(self):
        """Fetch chapters"""

        async with aiohttp.ClientSession() as session:

            self._d('fetch.chapters')
            chapters_meta = await self.fetch_chapters(self.url, session)

            self._d('fetch.pages')
            pages = await asyncio.gather(*(
                asyncio.ensure_future(self.fetch_pages(chapter, session))
                for chapter in chapters_meta
            ))

            return [
                Chapter(url=c.url, index=c.index, title=c.title,
                        volume=c.volume, _pages=p)
                for c, p in zip(chapters_meta, pages)
            ]

    @abstract
    async def fetch_chapters(self, url: str, session: aiohttp.ClientSession) -> List[Chapter]:
        """Retrieve chapters list"""

    @abstract
    async def fetch_pages(self, chapter: Chapter, session: aiohttp.ClientSession) -> List[Page]:
        """Retrieve chapter pages"""
