from pathlib import Path
from typing import Any, List, Tuple

from PIL import Image, ImageFile
from PyPDF2 import PdfFileMerger, PdfFileReader

from haku.export import Converter
from haku.meta import Chapter, Page

# fix truncated images error
# https://stackoverflow.com/questions/12984426/python-pil-ioerror-image-file-truncated-with-big-images
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Pdf(Converter):
    """Pdf converter"""

    def _convert_chapter(
        self,
        chapter: Chapter,
        pages: List[Tuple[Page, Image.Image]],
    ) -> bool:
        """Convert a chapter"""

        images = [image for _, image in pages]
        out = self.out.chapter(chapter, fmt="{index:g} {title}.pdf")

        with out.open("wb") as stream:
            images[0].save(
                stream,
                format="pdf",
                save_all=True,
                append_images=images[1:],
                resolution=100.0,
            )

        return True, (chapter, out)

    def _merge(self, chapters: List[Tuple[Chapter, Any]], out: Path, name: str):

        chapters = sorted(chapters, key=lambda t: t[0].index)

        merger = PdfFileMerger()
        for _, path in chapters:
            partial = PdfFileReader(str(path), "rb")
            merger.append(partial)

        out.mkdir(parents=True, exist_ok=True)
        out = out / f"{name}.pdf"

        with out.open("wb") as stream:
            merger.write(stream)
