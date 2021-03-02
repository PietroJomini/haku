from PyPDF2 import PdfFileMerger, PdfFileReader
from typing import Optional, IO, List, Union
from haku.meta import Chapter, Manga
from pathlib import Path
from PIL import Image


def _merge(pdfs: List[Path], out: Union[Path, IO[bytes]]):
    """Merge pdf files"""

    merger = PdfFileMerger()
    for pdf in pdfs:
        print(f'PDF {pdf}')
        partial = PdfFileReader(str(pdf), 'rb')
        merger.append(partial)

    out = str(out) if isinstance(out, Path) else out
    merger.write(out)


def chapter(ch: Chapter, path: Path, out: Optional[IO[bytes]] = None, out_path: Optional[Path] = None, pages_suffixes=['.png']):
    """Export chapter to pdf"""

    chapter_path = path / f'{ch.index} {ch.title}'

    pages = filter(
        lambda child: child.suffix in pages_suffixes,
        chapter_path.rglob('*')
    )

    images = []
    for page in sorted(pages, key=lambda page: int(page.stem)):
        image = Image.open(page)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        images.append(image)

    def _save_images(stream):
        images[0].save(
            stream,
            format='pdf',
            save_all=True,
            append_images=images[1:],
            resolution=100.0
        )

    if out is not None:
        _save_images(out)
    else:
        pdf_path = chapter_path if out_path is None else out_path
        if pdf_path.is_dir():
            pdf_path = pdf_path / f'{ch.index} {ch.title}.pdf'

        with(open(pdf_path, 'wb')) as out:
            _save_images(out)

    for image in images:
        image.close()
