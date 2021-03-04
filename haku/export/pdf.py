from io import RawIOBase
from pathlib import Path
from typing import IO, List, Union

from PIL import ImageFile
from PyPDF2 import PdfFileMerger, PdfFileReader

from haku.meta import Chapter
from haku.raw.fs import Reader
from haku.utils import ensure_bytesio

# TODO(me) Investigate
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _merge(pdfs: List[Path]) -> PdfFileMerger:
    """Merge pdf files"""

    merger = PdfFileMerger()
    for pdf in pdfs:
        partial = PdfFileReader(str(pdf), "rb")
        merger.append(partial)

    return merger


def chapter(
    chapter: Chapter,
    reader: Reader,
    out: Union[IO[bytes], Path],
    pages_suffixes: List[str] = [".png"],
) -> RawIOBase:
    """Export chapter to pdf"""

    images = list(
        map(
            lambda image: image[1],
            sorted(reader.chapter(chapter), key=lambda image: image[0].index),
        )
    )

    stream, temp = ensure_bytesio(out)

    images[0].save(
        stream, format="pdf", save_all=True, append_images=images[1:], resolution=100.0
    )

    for image in images:
        image.close()

    if temp:
        stream.close()
