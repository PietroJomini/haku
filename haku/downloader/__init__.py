from haku.meta import Page, Chapter
from haku.utils import eventh
from haku.fs import write_page
from pathlib import Path
from typing import Tuple
from io import BytesIO
from PIL import Image
import aiohttp
import asyncio
import ssl


class Downloader(eventh.Handler):
    """Downloader defaults"""

    RETRY_ON_CONNECTION_ERROR: bool = True
    RATE_LIMIT: int = 50
    ALLOWED_CONNECTION_ERRORS: Tuple[Exception] = (
        aiohttp.ClientError,
        ssl.SSLError
    )

    async def _page(self, session: aiohttp.ClientSession, page: Page) -> Image:
        """Page downloader async worker"""

        async with session.get(page.url) as response:
            raw = await response.read()
            stream = BytesIO(raw)
            image = Image.open(stream)
            stream.close()
            return image

    async def page(self, session: aiohttp.ClientSession, page: Page, path: Path):
        """Download and write page to disk"""

        self._d('page', page)

        try:
            image = await self._page(session, page)

        except self.ALLOWED_CONNECTION_ERRORS as err:
            self._d('page.error.allowed', page, err)
            if self.RETRY_ON_CONNECTION_ERROR:
                return await self.page(session, page, path)

        except Exception as err:
            self._d('page.error.not_allowed', page, err)

        else:
            self._d('page.write', page)
            write_page(page, image, path)

        finally:
            self._d('page.end', page)

    async def _chapter(self, session: aiohttp.ClientSession, chapter: Chapter, path: Path):
        """Chapter downloader async worker"""

        self._d('chapter')
        new_path = path / f'{chapter.index} {chapter.title}'
        tasks = (self.page(session, page, new_path) for page in chapter._pages)

        await asyncio.gather(*tasks)
        self._d('chapter.end')

    async def chapters(self, *chapters: Chapter, path: Path = Path.cwd()):
        """Download a set of chapters"""

        async with asyncio.Semaphore(self.RATE_LIMIT):
            async with aiohttp.ClientSession() as session:
                tasks = (self._chapter(session, chapter, path)
                         for chapter in chapters)

                await asyncio.gather(*tasks)
