import json
from typing import Optional

import toml
import yaml

from haku.meta import Manga


class Serializer:
    """Manga serializer"""

    def __init__(self, manga: Manga):
        self.manga = manga

    def to_dict(self, chapters: bool = True, pages: bool = True) -> dict:
        """Serialize to a python dict"""

        manga_dict = dict(
            url=self.manga.url,
            title=self.manga.title,
        )

        if self.manga.cover_url is not None:
            manga_dict["cover_url"] = self.manga.cover_url

        if chapters:
            manga_dict["chapters"] = []
            for chapter in self.manga.chapters:
                chapter_dict = dict(
                    url=chapter.url,
                    index=chapter.index,
                    title=chapter.title,
                    volume=chapter.volume,
                )

                if pages:
                    chapter_dict["pages"] = []
                    for page in chapter._pages:
                        chapter_dict["pages"].append(
                            dict(url=page.url, index=page.index)
                        )

                manga_dict["chapters"].append(chapter_dict)

        return manga_dict

    def json(
        self, chapters: bool = True, pages: bool = True, indent: Optional[int] = None
    ):
        """Serialize to json"""

        return json.dumps(self.to_dict(chapters=chapters, pages=pages), indent=indent)

    def yaml(self, chapters: bool = True, pages: bool = True):
        """Serialize to yaml"""

        return yaml.dump(self.to_dict(chapters=chapters, pages=pages))

    def toml(
        self, chapters: bool = True, pages: bool = True, indent: Optional[int] = None
    ):
        """Serialize to yaml"""

        return toml.dumps(self.to_dict(chapters=chapters, pages=pages))
