from typing import Union

from haku.meta import Manga
from haku.provider import Scraper, route
from haku.shelf import Filter, Shelf, StringifiedFilter
from haku.utils.cli import Console, Loader


def prepare_manga(
    scraper: Scraper,
    re: str,
    filters: str,
    ignore: str,
    pages: bool,
) -> Shelf:
    """Prepare th emanga with a shelf"""

    filters = Filter.true() if filters is None else StringifiedFilter.parse(filters)
    ignore = Filter.false() if ignore is None else StringifiedFilter.parse(ignore)
    f = filters & ~ignore

    scraper.provider.re_chapter_title = re or scraper.provider.re_chapter_title
    shelf = scraper.fetch_sync(f, fetch_pages=pages)

    return shelf


def rich_fetch(
    console: Console,
    url: str,
    re: str,
    apply_filter: str,
    ignore: str,
    pages: bool = False,
) -> Union[Manga, Scraper]:
    """Fetch the provider with a rich loader"""

    with Loader(console, "Fetching info"):
        scraper = route(url)
        shelf = prepare_manga(scraper, re, apply_filter, ignore, pages)
        return shelf.sort(), scraper
