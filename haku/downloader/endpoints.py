from haku.utils import write_image, eventh
from haku.meta import Page, Chapter
from typing import Tuple
from pathlib import Path
from io import BytesIO
from PIL import Image
import asyncio
import aiohttp
import ssl


class Endpoints(eventh.Handler):
    """Downloader defaults endpoints"""

    RETRY_ON_CONNECTION_ERROR: bool = True
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
            write_image(image, path, page.index)

        finally:
            self._d('page.end', page)

    async def chapter(self, session: aiohttp.ClientSession, chapter: Chapter, path: Path):
        """Download and write a chapter to disk"""

        self._d('chapter')
        tasks = (self.page(session, page, path) for page in chapter._pages)
        await asyncio.gather(*tasks)
        self._d('chapter.end')
