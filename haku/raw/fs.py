from pathlib import Path
from typing import Generator, Tuple, Union

from PIL import Image

from haku.meta import Chapter, Manga, Page
from haku.utils import cleanup_folder


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


class FTree:
    """Folders tree builder"""

    def __init__(
        self,
        root: Path,
        manga: Manga,
        fmt="{title}",
        dotman: Union[str, Dotman] = ".haku",
    ):
        self.root = root / fmt.format(title=manga.title, url=manga.url)
        self.dotman = (
            dotman
            if isinstance(dotman, Dotman)
            else Dotman(
                self.root,
                name=dotman,
            )
        )

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

    def __enter__(self):
        return self

    def __exit__(self, *_):
        cleanup_folder(self.root)


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
