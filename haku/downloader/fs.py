from haku.meta import Page, Chapter, Manga
from typing import Generator, Tuple
from pathlib import Path


class FTree:
    """Folders tree builder"""

    def __init__(self, root: Path, manga: Manga, fmt='{title}'):
        self.root = root / fmt.format(
            title=manga.title,
            url=manga.url
        )

    def chapter(self, chapter: Chapter, fmt='{index} {title}') -> Path:
        """Build chapter path"""

        return self.root / fmt.format(
            index=chapter.index,
            title=chapter.title,
            volume=chapter.volume
        )

    def flatten(self, *chapters: Chapter, fmt='{index} {title}') -> Generator[Tuple[Page, Path], None, None]:
        """Flatten all pages in a list with the related paths"""

        for chapter in chapters:
            path = self.chapter(chapter, fmt=fmt)
            for page in chapter._pages:
                yield page, path
