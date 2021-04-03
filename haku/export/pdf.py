from pathlib import Path
from typing import List, Optional, Tuple, Union

from PIL import Image, ImageFile
from PyPDF2 import PdfFileMerger, PdfFileReader

from haku.export import Converter
from haku.meta import Chapter, Manga, Page
from haku.raw.fs import FTree, Reader
from haku.shelf import Shelf

# fix truncated images error
# https://stackoverflow.com/questions/12984426/python-pil-ioerror-image-file-truncated-with-big-images
ImageFile.LOAD_TRUNCATED_IMAGES = True


class Pdf(Converter):
    """Pdf converter"""

    def __init__(
        self,
        manga: Union[Manga, Shelf],
        reader: Union[Reader, FTree],
        out: Union[FTree, Path],
        merge: bool = False,
        merge_out: Optional[Union[FTree, Path]] = None,
    ):
        super().__init__(manga, reader, out)

        self.merge = merge
        self.m_out = merge_out or self.out
        self.m_out = self.m_out if isinstance(self.m_out, Path) else self.m_out.root

    def _convert_chapter(
        self,
        chapter: Chapter,
        pages: List[Tuple[Page, Image.Image]],
    ) -> bool:
        """Convert a chapter"""

        images = [image for _, image in pages]
        out = self.out.chapter(chapter, fmt="{index:g} {title}.pdf")
        self.shared_list.append((out, chapter))

        with out.open("wb") as stream:
            images[0].save(
                stream,
                format="pdf",
                save_all=True,
                append_images=images[1:],
                resolution=100.0,
            )

        return True

    def _followup(self):
        """Merge chapters"""

        if not self.merge:
            return

        pdf_chapters = sorted(self.shared_list, key=lambda t: t[1].index)

        merger = PdfFileMerger()
        for path, _ in pdf_chapters:
            partial = PdfFileReader(str(path), "rb")
            merger.append(partial)

        self.m_out.mkdir(parents=True, exist_ok=True)
        out = self.m_out / f"{self.manga.title}.pdf"

        with out.open("wb") as stream:
            merger.write(stream)
