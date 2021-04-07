from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

import yaml


@dataclass
class Page:
    """Page meta"""

    url: int
    index: str

    def as_dict(self) -> Dict:
        """Serialize into a `dict`"""

        return asdict(self)

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

        dictified = asdict(self)

        if not add_pages:
            del dictified["pages"]

        return dictified

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

    cover: Optional[str] = None
    chapters: Optional[List[Chapter]] = None

    def as_dict(self, add_chapters: bool = True, add_pages: bool = True) -> Dict:
        """Serialize into a `dict`"""

        dictified = asdict(self)

        if add_chapters:
            dictified["chapters"] = [c.as_dict(add_pages) for c in self.chapters]
        else:
            del dictified["chapters"]

        return dictified

    def yaml(
        self,
        add_chapters: bool = True,
        add_pages: bool = True,
    ) -> str:
        """Serialize as json"""

        dictified = self.as_dict(add_chapters, add_pages)
        return yaml.dump(dictified)

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
            cover=src["cover"],
            chapters=chapters,
        )

    @staticmethod
    def from_yaml(src: str):
        """Parse a yaml string into a Manga object"""

        dictified = yaml.safe_load(src)
        return Manga.from_dict(dictified)
