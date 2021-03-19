import asyncio
import re
from importlib import import_module
from io import BytesIO
from typing import List, Type

import aiohttp
from bs4 import BeautifulSoup
from PIL import Image

from haku.exceptions import NoProviderFound
from haku.meta import Chapter, Manga, Page
from haku.providers import providers
from haku.raw.endpoints import Endpoints
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


class Provider(eventh.Handler):
    """Provider default"""

    name: str
    pattern: str

    enabled: bool = True
    endpoints: Type[Endpoints] = Endpoints

    def __init__(self, url: str):
        self.url = url
        self.helpers = Helpers()

    def fetch_sync(self) -> Manga:
        """Fetch the manga"""

        return asyncio.run(self.fetch())

    async def fetch(self) -> Manga:
        """Fetch the manga"""

        async with aiohttp.ClientSession() as session:

            chapters_partials = await self.fetch_chapters(session, self.url)
            pages_futures = (
                asyncio.ensure_future(self.fetch_pages(session, chapter))
                for chapter in chapters_partials
            )

            chapters = [
                Chapter(
                    url=c.url,
                    title=c.title,
                    index=c.index,
                    volume=c.volume,
                    pages=p,
                )
                for c, p in zip(
                    chapters_partials,
                    await asyncio.gather(*pages_futures),
                )
            ]

            return Manga(
                title=await self.fetch_title(session, self.url),
                cover=await self.fetch_cover(session, self.url),
                chapters=chapters,
                url=self.url,
            )

    @eventh.Handler.async_event("title")
    async def fetch_title(self, session: aiohttp.ClientSession, url: str) -> str:
        """Retrieve title"""

        return await self._fetch_title(session, url)

    @abstract
    async def _fetch_title(self, session: aiohttp.ClientSession, url: str) -> str:
        """Custom provider API :: Retrieve title"""

    @eventh.Handler.async_event("cover")
    async def fetch_cover(self, session: aiohttp.ClientSession, url: str) -> str:
        """Retrieve cover"""

        return await self._fetch_cover(session, url)

    @abstract
    async def _fetch_cover(self, session: aiohttp.ClientSession, url: str) -> str:
        """Custom provider API :: Retrieve cover"""

    @eventh.Handler.async_event("chapters")
    async def fetch_chapters(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[Chapter]:
        """Retrieve chapters list"""

        return await self._fetch_chapters(session, url)

    @abstract
    async def _fetch_chapters(
        self, session: aiohttp.ClientSession, url: str
    ) -> List[Chapter]:
        """Custom provider API :: Retrieve chapters list"""

    @eventh.Handler.async_event("pages")
    async def fetch_pages(
        self, session: aiohttp.ClientSession, chapter: Chapter
    ) -> List[Page]:
        """Retrieve pages list"""

        return await self._fetch_pages(session, chapter)

    @abstract
    async def _fetch_pages(
        self, session: aiohttp.ClientSession, chapter: Chapter
    ) -> List[Page]:
        """Custom provider API :: Retrieve pages list"""


def route(r: str) -> Type[Provider]:
    """Try to match a provider from the enabled providers"""

    for provider in providers:
        candidate = import_module(f"haku.providers.{provider}").provider
        if candidate.enabled and re.match(candidate.pattern, r):
            return candidate(r)

    raise NoProviderFound(f'No provider match route "{r}"')
