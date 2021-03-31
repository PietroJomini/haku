import click

from haku.meta import Manga
from haku.provider import route
from haku.ui.cli.common import prepare_manga, rich_fetch
from haku.utils.cli import Console
from haku.utils.cli.renderable import Text
from haku.utils.cli.table import Table


def rich_info(
    console: Console,
    manga: Manga,
    show_chapters: bool,
    show_urls: bool,
    show_volumes: bool,
):
    """Format manga as a rich renderable"""

    table = Table()
    table.add_row(Text("META", expand=True))

    meta = [Text("Title"), Text("Url"), Text("Cover")]
    meta_values = [manga.title, manga.url, manga.cover]

    info = Table()
    info.add_column(*(meta if show_urls else meta[:-2]), same_width=True)
    info.add_column(*(meta_values if show_urls else meta_values[:-2]))
    table += info

    columns = [
        [Text("Volume")],
        [Text("Index")],
        [Text("Title", expand=not show_urls)],
        ["Url"],
    ]
    for chapter in manga.chapters:
        columns[0].append(Text(f"{chapter.volume:g}"))
        columns[1].append(Text(f"{chapter.index:g}"))
        columns[2].append(Text(chapter.title, expand=not show_urls))
        columns[3].append(chapter.url)

    table.add_row(Text("CHAPTERS", expand=True))

    chapters = Table()
    if show_volumes:
        chapters.add_column(*columns[0], same_width=True)
    chapters.add_column(*columns[1], same_width=True)
    chapters.add_column(*columns[2], same_width=show_urls)
    if show_urls:
        chapters.add_column(*columns[3])

    console.print(table + chapters)


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

    shelf, _ = rich_fetch(Console(columns=100), url, re, apply_filter, ignore)
    rich_info(Console(), shelf.manga, show_chapters, show_urls, show_volumes)
