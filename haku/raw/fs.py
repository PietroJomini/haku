import shutil
from pathlib import Path
from typing import Generator, Tuple

from PIL import Image

from haku.meta import Chapter, Manga, Page


class FTree:
    """Folders tree builder"""

    def __init__(self, root: Path, manga: Manga, fmt="{title}"):
        self.root = root / fmt.format(title=manga.title, url=manga.url)
        self._is_tmp = False

    def chapter(self, chapter: Chapter, fmt="{index:g} {title}") -> Path:
        """Build chapter path"""

        return self.root / fmt.format(
            index=chapter.index, title=chapter.title, volume=chapter.volume
        )

    def flatten(
        self, *chapters: Chapter, fmt="{index:g} {title}"
    ) -> Generator[Tuple[Page, Path], None, None]:
        """Flatten all pages in a list with the related paths"""

        for chapter in chapters:
            path = self.chapter(chapter, fmt=fmt)
            for page in chapter._pages:
                yield page, path

    def cleanup(self):
        """Cleanup root tree"""

        shutil.rmtree(self.root)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.cleanup()


class Reader:
    """Folder tree reader"""

    def __init__(self, tree: FTree):
        self.tree = tree

    def chapter(
        self, chapter: Chapter, mode="RGB", ext="png"
    ) -> Generator[Tuple[Page, Image.Image], None, None]:
        """Read images from chapter"""

        for page, path in self.tree.flatten(chapter):
            image = Image.open(path / f"{page.index}.{ext}")
            if image.mode != mode:
                image = image.convert(mode)
            yield page, image
