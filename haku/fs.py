from haku.meta import Page
from pathlib import Path


def write_page(page: Page, path: Path, fmt='png'):
    """Writes a page to disk"""

    path.mkdir(parents=True, exist_ok=True)
    page._raw.save(str(path / f'{page.index}.{fmt}'), format=fmt)
