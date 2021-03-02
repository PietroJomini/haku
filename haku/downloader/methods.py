from haku.downloader import Downloader
from haku.provider import Provider
from haku.meta import Chapter
from haku.utils import chunks
from pathlib import Path
import asyncio
import aiohttp


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
