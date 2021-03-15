from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageFile
from PyPDF2 import PdfFileMerger, PdfFileReader

from haku.export import Converter
from haku.meta import Chapter, Page

# TODO(me) Investigate
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _merge(pdfs: List[Path]) -> PdfFileMerger:
    """Merge pdf files"""

    merger = PdfFileMerger()
    for pdf in pdfs:
        partial = PdfFileReader(str(pdf), "rb")
        merger.append(partial)

    return merger


class Pdf(Converter):
    """Pdf converter"""

    def _convert_chapter(
        self, chapter: Chapter, pages: List[Tuple[Page, Image.Image]]
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

        return True
