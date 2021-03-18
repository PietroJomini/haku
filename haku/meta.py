from dataclasses import dataclass
from typing import Dict, List, Optional, Type

import yaml
from PIL import Image


@dataclass
class Page:
    """Page meta"""

    url: int
    index: str

    def as_dict(self) -> Dict:
        """Serialize into a `dict`"""

        return dict(url=self.url, index=self.index)

    @staticmethod
    def from_dict(src: Dict):
        """Parse a dict into a Page object"""

        return Page(url=src["url"], index=src["index"])


@dataclass
class Chapter:
    """Chapter meta"""

    url: str
    title: str
    index: float

    volume: Optional[float] = None
    pages: Optional[List[Page]] = None

    def as_dict(self, add_pages: bool = True) -> Dict:
        """Serialize into a `dict`"""

        pages = (
            [page.as_dict() for page in self.pages]
            if add_pages and self.pages is not None
            else None
        )

        return dict(
            url=self.url,
            title=self.title,
            index=self.index,
            volume=self.volume,
            pages=pages,
        )

    @staticmethod
    def from_dict(src: Dict):
        """Parse a dict into a Chapter object"""

        pages = (
            list(map(Page.from_dict, src["pages"]))
            if src["pages"] is not None
            else None
        )

        return Chapter(
            url=src["url"],
            title=src["title"],
            index=src["index"],
            volume=src["volume"],
            pages=pages,
        )


@dataclass
class Manga:
    """Manga meta"""

    url: str
    title: str

    cover_url: Optional[str] = None
    cover: Optional[Type[Image.Image]] = None
    chapters: Optional[List[Chapter]] = None

    def as_dict(self, add_chapters: bool = True, add_pages: bool = True) -> Dict:
        """Serialize into a `dict`"""

        chapters = (
            [chapter.as_dict(add_pages) for chapter in self.chapters]
            if add_chapters and self.chapters is not None
            else None
        )

        return dict(
            url=self.url,
            title=self.title,
            cover_url=self.cover_url,
            chapters=chapters,
        )

    def yaml(
        self,
        add_chapters: bool = True,
        add_pages: bool = True,
    ) -> str:
        """Serialize as json"""

        return yaml.dump(self.as_dict(add_chapters, add_pages))

    @staticmethod
    def from_dict(src: Dict):
        """Parse a dict into a Manga object"""

        chapters = (
            list(map(Chapter.from_dict, src["chapters"]))
            if src["chapters"] is not None
            else None
        )

        return Manga(
            url=src["url"],
            title=src["title"],
            cover_url=src["cover_url"],
            chapters=chapters,
        )

    @staticmethod
    def from_yaml(src: str):
        """Parse a yaml string into a Manga object"""

        dictified = yaml.safe_load(src)
        return Manga.from_dict(dictified)
