from typing import Tuple, Type, Union, Callable, List, Generator
from haku.utils import eventh, write_image, chunks
from haku.meta import Page, Chapter, Manga
from haku.raw.endpoints import Endpoints
from haku.provider import Provider
from haku.raw.fs import FTree
from pathlib import Path
from io import BytesIO
from PIL import Image
import aiohttp
import asyncio
import ssl


class Method():
    """Download methods"""

    @staticmethod
    def batch(size: int = 0) -> Callable[[Endpoints, FTree, Manga], None]:
        """Download chapters in chunk"""

        async def method(endpoints: Endpoints, tree: FTree, manga: Manga):
            pages = list(tree.flatten(*manga.chapters))
            actual_size = len(pages) if size == 0 else size
            for chunk in chunks(pages, actual_size):
                async with aiohttp.ClientSession() as session:
                    await endpoints.pages(session, *chunk)

        return method


class Downloader(eventh.Handler):
    """Downloader"""

    RATE_LIMIT: int = 200
    endpoints: Type[Endpoints] = Endpoints

    @staticmethod
    def from_provider(provider: Provider, manga: Manga, root: Union[Path, FTree]):
        """Instantiate a downloader from a provider"""

        return Downloader(provider.endpoints(), manga, root)

    def __init__(self, endpoints: Endpoints, manga: Manga, root: Union[Page, FTree]):
        self.tree = root if isinstance(root, FTree) else FTree(root, manga)
        self.endpoints = endpoints
        self.manga = manga

    def download(self, method: Callable = Method.batch()):
        """Download the manga following the preferred method"""

        async def runner():
            async with asyncio.Semaphore(self.RATE_LIMIT):
                await method(self.endpoints, self.tree, self.manga)

        asyncio.run(runner())
