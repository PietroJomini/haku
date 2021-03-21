import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Column, Table

from haku.meta import Manga
from haku.provider import Scraper, route
from haku.shelf import StringifiedFilter


def rich_info(manga: Manga, show_urls: bool):
    """Create rich table with manga info"""

    out = f"Title: [b]{manga.title}[/b]"

    urls = ["", f"Url: {manga.url}\n"]
    if manga.cover is not None:
        urls.append(f"Cover url: {manga.cover}")

    if show_urls:
        out += "\n".join(urls)

    return Panel.fit(out)


def rich_chapters(manga: Manga, show_urls: bool, show_volumes: bool):
    """Create rich table with chapters"""

    columns = [
        Column("Volume", justify="right") if show_volumes else None,
        Column("Index", justify="right"),
        Column("Title"),
        Column("Url") if show_urls else None,
    ]

    table = Table(*filter(lambda c: c is not None, columns), box=box.ROUNDED)

    for chapter in manga.chapters:
        row = [
            f"{chapter.volume:g}" if show_volumes else None,
            f"{chapter.index:g}",
            chapter.title,
            chapter.url if show_urls else None,
        ]

        table.add_row(*filter(lambda r: r is not None, row))

    return table


def prepare_manga(
    scraper: Scraper,
    re: str,
    filters: str,
    ignore: str,
    sort: bool,
    pages: bool,
) -> Manga:
    """Prepare th emanga with a shelf"""

    if re != "":
        scraper.provider.re_chapter_title = re

    if filters != "":
        f = StringifiedFilter.parse(filters) & ~StringifiedFilter.parse(ignore)
        shelf = scraper.fetch_sync(f, fetch_pages=pages)
    else:
        shelf = scraper.fetch_sync(fetch_pages=pages)

    if sort:
        shelf.sort()

    return shelf.manga


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
    "-u",
    "--show-urls",
    is_flag=True,
    help="Display url in rich mode",
)
@click.option(
    "-c",
    "--chapters",
    is_flag=True,
    help="Display chapters",
)
@click.option(
    "-v",
    "--show-volumes",
    is_flag=True,
    help="Display chapters volume in rich mode",
)
@click.option(
    "-p",
    "--pages",
    is_flag=True,
    help="Display pages in non-rich modes",
)
@click.option(
    "-f",
    "--apply-filter",
    default="",
    help="Apply stringified filter",
)
@click.option(
    "-i",
    "--ignore",
    default="",
    help="Ignore from stringified filter",
)
@click.option(
    "-r",
    "--re",
    default="",
    help='Regex used to parse the title. Must include the named groups: "index", '
    + 'and can include the named groups: ["volume", "title"]',
)
def info(
    url: str,
    out: str,
    chapters: bool,
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
        manga = prepare_manga(scraper, re, apply_filter, ignore, False, pages)
        print(manga.yaml(chapters, pages))
        return

    console = Console()

    with console.status("Fetching info", spinner="bouncingBar", spinner_style=""):
        scraper = route(url)
        manga = prepare_manga(scraper, re, apply_filter, ignore, True, False)

    console.print(
        rich_chapters(manga, show_urls, show_volumes)
        if chapters
        else rich_info(manga, show_urls)
    )
