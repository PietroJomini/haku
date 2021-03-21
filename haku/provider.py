import asyncio
import re
from importlib import import_module
from io import BytesIO
from typing import List, Optional, Type

import aiohttp
from bs4 import BeautifulSoup
from PIL import Image

from haku.exceptions import NoProviderFound
from haku.meta import Chapter, Manga, Page
from haku.providers import providers
from haku.raw.endpoints import Endpoints
from haku.shelf import Filter, Shelf
from haku.utils import abstract, eventh


class Helpers:
    """Provider helpers"""

    def __init__(self):
        self.cached_webpages = {}
        self.cached_soups = {}

    async def scrape(
        self, session: aiohttp.ClientSession, url: str, allow_cached=True
    ) -> str:
        """Scrape a webpage"""

        if url in self.cached_webpages and allow_cached:
            print(f"Using cached {url}")
            return self.cached_webpages[url]

        async with session.get(url) as response:
            content = await response.text()
            self.cached_webpages[url] = content
            return content

    async def scrape_and_cook(
        self,
        session: aiohttp.ClientSession,
        url: str,
        allow_cached=True,
        parser="html.parser",
    ) -> BeautifulSoup:
        """Scrape a webpage into a BeautifulSoup soup"""

        if url in self.cached_soups and allow_cached:
            return self.cached_soups[url]

        content = await self.scrape(session, url, allow_cached=allow_cached)
        soup = BeautifulSoup(content, parser)
        self.cached_soups[url] = soup
        return soup

    async def fetch_image(self, session: aiohttp.ClientSession, url: str) -> Image:
        """Scrape an image into a PIL Image"""

        async with session.get(url) as response:
            raw = await response.read()
            stream = BytesIO(raw)
            image = Image.open(stream)
            return image


class Provider:
    """Provider defaults"""

    name: str
    pattern: str

    enabled: bool = True
    endpoints: Type[Endpoints] = Endpoints

    def __init__(self):
        self.helpers = Helpers()

    @abstract
    async def fetch_title(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> str:
        """Retrieve title"""

    @abstract
    async def fetch_cover(
        self,
        session: aiohttp.ClientSession,
        url: str,
    ) -> str:
        """Retrieve cover"""

    @abstract
    async def fetch_chapters(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[Chapter]:
        """Retrieve chapters list"""

    @abstract
    async def fetch_pages(
        self, session: aiohttp.ClientSession, chapter: Chapter
    ) -> List[Page]:
        """Retrieve pages list"""


class Scraper(eventh.Handler):
    """Meta scraper"""

    def __init__(self, url: str, provider: Provider):
        self.url = url
        self.provider = provider

    def fetch_sync(self, f: Optional[Filter] = None) -> Shelf:
        """Fetch the manga"""

        return asyncio.run(self.fetch(f))

    async def fetch(self, f: Optional[Filter] = None) -> Shelf:
        """Fetch the manga"""

        async with aiohttp.ClientSession() as session:

            manga = Manga(
                title=await self.fetch_title(session, self.url),
                cover=await self.fetch_cover(session, self.url),
                chapters=await self.fetch_chapters(session, self.url),
                url=self.url,
            )

            shelf = Shelf(manga)
            if f is not None:
                shelf.filter(f)

            pages_futures = (
                asyncio.ensure_future(self.fetch_pages(session, chapter))
                for chapter in shelf.manga.chapters
            )

            await asyncio.gather(*pages_futures)
            return shelf

    @eventh.Handler.async_event("title")
    async def fetch_title(self, session: aiohttp.ClientSession, url: str) -> str:
        """Retrieve title"""

        return await self.provider.fetch_title(session, url)

    @eventh.Handler.async_event("cover")
    async def fetch_cover(self, session: aiohttp.ClientSession, url: str) -> str:
        """Retrieve cover"""

        return await self.provider.fetch_cover(session, url)

    @eventh.Handler.async_event("chapters")
    async def fetch_chapters(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[Chapter]:
        """Retrieve chapters list"""

        return await self.provider.fetch_chapters(session, url)

    @eventh.Handler.async_event("pages")
    async def fetch_pages(
        self, session: aiohttp.ClientSession, chapter: Chapter
    ) -> Chapter:
        """Retrieve pages list"""

        chapter.pages = await self.provider.fetch_pages(session, chapter)
        return chapter


def route(url: str) -> Scraper:
    """Try to match a provider from the enabled providers"""

    for provider in providers:
        candidate = import_module(f"haku.providers.{provider}").provider
        if candidate.enabled and re.match(candidate.pattern, url):
            return Scraper(url, candidate())

    raise NoProviderFound(f'No provider match route "{url}"')
