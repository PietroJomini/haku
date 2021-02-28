from haku.meta import Page
from pathlib import Path
from PIL import Image


def write_page(page: Page, image: Image, path: Path, fmt='png', cleanup=True):
    """Writes a page to disk"""

    path.mkdir(parents=True, exist_ok=True)
    image.save(str(path / f'{page.index}.{fmt}'), format=fmt)

    if cleanup:
        image.close()
        del image
