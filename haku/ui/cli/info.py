import click
from rich import box
from rich.console import Console, RenderGroup
from rich.panel import Panel
from rich.table import Column, Table

from haku.meta import Manga
from haku.provider import route
from haku.ui.cli.common import prepare_manga, rich_fetch


def rich_info(manga: Manga, show_chapters: bool, show_urls: bool, show_volumes: bool):
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

    if not show_urls:
        meta = meta[:-2]

    meta = Panel.fit("\n".join(meta), box=box.SIMPLE)
    if not show_chapters:
        return meta

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
    if not show_volumes:
        chapters.columns = chapters.columns[1:]

    return RenderGroup(meta, chapters)


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
    "-c",
    "--show-chapters",
    is_flag=True,
    help="Display chapters [applied only in RICH format]",
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
    show_chapters: bool,
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
    console.print(Panel(rich_info(manga, show_chapters, show_urls, show_volumes)))
