from haku.utils import eventh, chunks
from haku.meta import Page, Chapter
from haku.fs import write_page
from pathlib import Path
from io import BytesIO
from PIL import Image
import aiohttp
import asyncio


class Downloader(eventh.Handler):
    """Downloader defaults"""

    RETRY_ON_CONNECTION_ERROR: bool = True
    RATE_LIMIT: int = 50

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

        except aiohttp.ClientError as err:
            self._d('page.error.aiohttp', page, err)
            if self.RETRY_ON_CONNECTION_ERROR:
                return await self.page(session, page, path)

        except Exception as err:
            self._d('page.error.generic', page, err)

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


def simple(downloader: Downloader, *chapters: Chapter, path: Path = Path.cwd()):
    """Download a set of chapters in parallel"""

    asyncio.run(downloader.chapters(*chapters, path=path))


async def _chunked_single_session(downloader: Downloader, *chapters: Chapter, path: Path = Path.cwd(), chunk_size: int = 1):
    """Download a set of chapters in chunk, with one session"""

    async with asyncio.Semaphore(downloader.RATE_LIMIT):
        async with aiohttp.ClientSession() as session:
            for chunk in chunks(chapters, chunk_size):
                tasks = (downloader._chapter(session, chapter, path)
                         for chapter in chunk)

                await asyncio.gather(*tasks)


def _chunked_k_session(downloader: Downloader, *chapters: Chapter, path: Path = Path.cwd(), chunk_size: int = 1):
    """Download a set of chapters in chunk, with multiple sessions"""

    for chunk in chunks(chapters, chunk_size):
        asyncio.run(downloader.chapters(*chunk, path=path))


def chunked(downloader: Downloader, *chapters: Chapter, path: Path = Path.cwd(), chunk_size: int = 1, single_session: bool = False):
    """Download a set of chapters in chunks"""

    if single_session:
        asyncio.run(_chunked_single_session(
            downloader, *chapters, path=path, chunk_size=chunk_size))
    else:
        _chunked_k_session(downloader, *chapters,
                           path=path, chunk_size=chunk_size)
