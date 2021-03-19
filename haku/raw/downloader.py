import asyncio
from pathlib import Path
from typing import Callable, Optional, Union

import aiohttp

from haku.meta import Manga
from haku.provider import Provider
from haku.raw.endpoints import Endpoints
from haku.raw.fs import FTree
from haku.shelf import Shelf
from haku.utils import chunks, tmpdir


class Method:
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


class Downloader:
    """Downloader"""

    def __init__(
        self,
        endp: Union[Endpoints, Provider],
        manga: Union[Manga, Shelf],
        root: Optional[Union[Path, FTree]] = tmpdir(),
    ):
        self.endpoints = endp if isinstance(endp, Endpoints) else endp.endpoints()
        self.manga = manga if isinstance(manga, Manga) else manga.manga
        self.tree = root if isinstance(root, FTree) else FTree(root, self.manga)

    def download(
        self,
        method: Callable = Method.batch(),
        rate_limit: int = 200,
        setup_recovery_plan: bool = True,
    ) -> FTree:
        """Download the manga with the given method"""

        if setup_recovery_plan:
            self.tree.dotman.dump(self.manga)

        async def runner():
            async with asyncio.Semaphore(rate_limit):
                await method(self.endpoints, self.tree, self.manga)

        asyncio.run(runner())

        return self.tree
