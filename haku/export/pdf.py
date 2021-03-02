from PyPDF2 import PdfFileMerger, PdfFileReader
from typing import Optional, IO, List, Union
from haku.utils import ensure_bytesio
from haku.meta import Chapter, Manga
from io import BytesIO, RawIOBase
from PIL import Image, ImageFile
from haku.raw.fs import Reader
from pathlib import Path


# TODO(me) Investigate
ImageFile.LOAD_TRUNCATED_IMAGES = True


def _merge(pdfs: List[Path]) -> PdfFileMerger:
    """Merge pdf files"""

    merger = PdfFileMerger()
    for pdf in pdfs:
        partial = PdfFileReader(str(pdf), 'rb')
        merger.append(partial)

    return merger


def chapter(chapter: Chapter, reader: Reader, out: Union[IO[bytes], Path], pages_suffixes: List[str] = ['.png']) -> RawIOBase:
    """Export chapter to pdf"""

    images = list(map(
        lambda image: image[1],
        sorted(
            reader.chapter(chapter),
            key=lambda image: image[0].index
        )
    ))

    stream, temp = ensure_bytesio(out)

    images[0].save(
        stream,
        format='pdf',
        save_all=True,
        append_images=images[1:],
        resolution=100.0
    )

    for image in images:
        image.close()

    if temp:
        stream.close()
