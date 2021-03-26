import asyncio
import ssl
from io import BytesIO
from pathlib import Path
from typing import Dict, Tuple

import aiohttp
from PIL import Image

from haku.meta import Page
from haku.utils import eventh, write_image


class Endpoints(eventh.Handler):
    """Downloader endpoints"""

    RETRY_ON_CONNECTION_ERROR: bool = True
    ALLOWED_CONNECTION_ERRORS: Tuple[Exception] = (aiohttp.ClientError, ssl.SSLError)

    async def get_page(
        self,
        session: aiohttp.ClientSession,
        page: Page,
        headers: Dict[str, str],
    ) -> Image:
        """Page downloader async worker"""

        async with session.get(page.url, headers=headers) as response:
            raw = await response.read()
            stream = BytesIO(raw)
            image = Image.open(stream)
            return image

    @eventh.Handler.event("page", wrap_async=True)
    async def page(self, session: aiohttp.ClientSession, page: Page, path: Path):
        """Download and write a page to disk"""

        try:
            headers = self.get_headers(page.url)
            image = await self.get_page(session, page, headers)

        except self.ALLOWED_CONNECTION_ERRORS as err:
            self.dispatch("page.error.allowed", page, err)
            if self.RETRY_ON_CONNECTION_ERROR:
                return await self.page(session, page, path)

        except Exception as err:
            self.dispatch("page.error.not_allowed", page, err)

        else:
            self.dispatch("page.write", page)
            write_image(image, path)

    async def pages(self, session: aiohttp.ClientSession, *pages: Tuple[Page, Path]):
        """Download a d write pages to disk"""

        tasks = (self.page(session, page, path) for page, path in pages)
        await asyncio.gather(*tasks)
