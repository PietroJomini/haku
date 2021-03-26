import asyncio
from pathlib import Path
from typing import Generator, List, Optional, Tuple

from PIL import Image

from haku.meta import Chapter, Manga, Page
from haku.utils import cleanup_folder, safe_path


class Dotman:
    """Dotfile manager"""

    def __init__(self, root: Path, name=".haku"):
        self.name = name
        self.root = root

    def dump(self, manga: Manga):
        """Dump serialized manga to dotfile"""

        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / self.name

        with path.open("w") as dotfile:
            dotfile.write(manga.yaml())

    def read(self) -> Manga:
        """Read manga from dotfile"""

        path = self.root / self.name
        content = path.read_text()
        return Manga.from_yaml(content)


class FTree:
    """Raw folder tree generator"""

    fmt_chapter: str = "{index:g} {title}"
    fmt_page: str = "{index}.{ext}"
    fmt_cover: str = "cover.{ext}"

    def __init__(
        self,
        root: Path,
        manga: Manga,
        fmt="{title}",
        ext: str = "png",
        dotman: Optional[Dotman] = None,
    ):
        self.ext = ext
        self.manga = manga
        self.root = root / safe_path(fmt.format(title=manga.title))
        self.dotman = dotman or Dotman(self.root)

    def chapter(self, chapter: Chapter, fmt: Optional[str] = None) -> Path:
        """Get chapter path"""

        fmt = fmt or self.fmt_chapter
        path = fmt.format(
            index=chapter.index,
            title=chapter.title,
            volume=chapter.volume,
        )

        return self.root / safe_path(path)

    def flatten(
        self,
        *chapters: Chapter,
        fmt: Optional[str] = None,
        fmt_page: Optional[str] = None,
    ) -> Generator[Tuple[Page, Path], None, None]:
        """Flatten pages and paths in a list"""

        fmt = fmt or self.fmt_chapter
        fmt_page = fmt_page or self.fmt_page

        for chapter in chapters:
            path = self.chapter(chapter, fmt)
            for page in chapter.pages:
                page_path = fmt_page.format(index=page.index, ext=self.ext)
                yield page, path / safe_path(page_path)

    def cover(self, fmt: Optional[str] = None):
        """Get cover path"""

        fmt = fmt or self.fmt_cover
        return self.root / safe_path(fmt.format(ext=self.ext))

    def __enter__(self):
        return self

    def __exit__(self, *_):
        cleanup_folder(self.root)


class Reader:
    """Raw folder tree reader"""

    def __init__(self, tree: FTree):
        self.tree = tree

    async def chapter(
        self, chapter: Chapter, mode: str = "RGB"
    ) -> List[Tuple[Page, Image.Image]]:
        """Read images from chapter"""

        tasks = (
            asyncio.ensure_future(self.page(page, path))
            for page, path in self.tree.flatten(chapter)
        )

        return await asyncio.gather(*tasks)

    async def page(
        self, page: Page, path: Path, mode: str = "RGB"
    ) -> List[Tuple[Page, Image.Image]]:
        """Read page from disk"""

        image = Image.open(path)
        if image.mode != mode:
            image = image.convert(mode)
        return page, image

    def missing(self) -> Manga:
        """Find missing pages in directory"""

        manga = Manga(**self.tree.manga.as_dict())
        manga.chapters = []

        for chapter in self.tree.manga.chapters:
            m_chapter = Chapter(**chapter.as_dict())
            m_chapter.pages = []

            for page, path in self.tree.flatten(chapter):
                if not path.is_file():
                    m_chapter.pages.append(page)

            manga.chapters.append(m_chapter)

        return manga
