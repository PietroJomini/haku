from typing import Optional, IO, List, Union
from haku.meta import Chapter, Manga
from haku.downloader.fs import Reader
from pathlib import Path
from PIL import Image
from io import BytesIO, RawIOBase
from haku.utils import ensure_bytesio


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

    if temp:
        stream.close()
