from rich.console import Console

from haku.meta import Manga
from haku.provider import Scraper, route
from haku.shelf import Filter, Shelf, StringifiedFilter


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
) -> Manga:
    """Fetch the provider with a rich loader"""

    with console.status("Fetching info", spinner="bouncingBar", spinner_style=""):
        shelf = prepare_manga(route(url), re, apply_filter, ignore, False)
        return shelf.sort().manga
