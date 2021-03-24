import click
from rich import box
from rich.console import Console, RenderGroup
from rich.panel import Panel
from rich.table import Column, Table

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


def rich_info(manga: Manga, show_urls: bool, show_volumes: bool):
    """Format manga as a rich renderable"""

    meta = [
        f"Title: [b]{manga.title}[/b]",
        f"Url: [b]{manga.url}[/b]",
        f"Cover: [b]{manga.cover}[/b]",
    ]

    columns = [
        Column("Volume", justify="right"),
        Column("Index", justify="right"),
        Column("Title"),
        Column("Url"),
    ]

    chapters = Table(*columns, box=box.MINIMAL)
    for chapter in manga.chapters:
        chapters.add_row(
            f"{chapter.volume:g}",
            f"{chapter.index:g}",
            chapter.title,
            chapter.url,
        )

    if not show_urls:
        chapters.columns = chapters.columns[:-1]
        meta = meta[:-2]
    if not show_volumes:
        chapters.columns = chapters.columns[1:]

    meta = Panel.fit("\n".join(meta), box=box.SIMPLE)
    return Panel(RenderGroup(meta, chapters))


@click.command()
@click.argument("url")
@click.option(
    "-o",
    "--out",
    default="RICH",
    type=click.Choice(["RICH", "YAML"], case_sensitive=False),
    help="Output format",
    show_default=True,
)
@click.option(
    "-v",
    "--show-volumes",
    is_flag=True,
    help="Display volume [applied only in RICH format]",
)
@click.option(
    "-u",
    "--show-urls",
    is_flag=True,
    help="Display urls [applied only in RICH format]",
)
@click.option(
    "-p",
    "--pages",
    is_flag=True,
    help="Display pages [applied only in YAML format]",
)
@click.option(
    "-f",
    "--filter",
    "apply_filter",
    help="Apply filter",
)
@click.option(
    "-i",
    "--ignore",
    help="Ignore filtered instances",
)
@click.option(
    "-r",
    "--re",
    help='Regex used to parse the title. Must include the named groups: "index", '
    + 'and can include the named groups: ["volume", "title"]',
)
def info(
    url: str,
    out: str,
    pages: bool,
    show_urls: bool,
    show_volumes: bool,
    apply_filter: str,
    ignore: str,
    re: str,
):
    """TODO(me) better description"""

    if out == "YAML":
        scraper = route(url)
        shelf = prepare_manga(scraper, re, apply_filter, ignore, pages)
        print(shelf.manga.yaml(add_chapters=True, add_pages=pages))
        return

    console = Console()
    manga = rich_fetch(console, url, re, apply_filter, ignore)
    console.print(rich_info(manga, show_urls, show_volumes))
