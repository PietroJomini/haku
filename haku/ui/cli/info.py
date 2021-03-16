import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Column, Table

from haku.export.serialize import Serializer
from haku.meta import Manga
from haku.provider import route
from haku.shelf import Shelf, StringifiedFilter


def rich_info(manga: Manga, show_urls: bool):
    """Create rich table with manga info"""

    out = f"Title: [b]{manga.title}[/b]"

    urls = ["", f"Url: {manga.url}\n"]
    if manga.cover_url is not None:
        urls.append(f"Cover url: {manga.cover_url}")

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


def prepare_manga(manga: Manga, filters: str, ignore: str, sort: bool = False) -> Manga:
    """Prepare th emanga with a shelf"""

    shelf = Shelf(manga)

    if filters != "":
        shelf.filter(StringifiedFilter.parse(filters))
        shelf.filter(~StringifiedFilter.parse(ignore))

    if sort:
        shelf.sort()

    return shelf.manga


@click.command()
@click.argument("url")
@click.option(
    "-o",
    "--out",
    default="RICH",
    type=click.Choice(["RICH", "JSON", "TOML", "YAML"], case_sensitive=False),
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
def info(
    url: str,
    out: str,
    chapters: bool,
    pages: bool,
    show_urls: bool,
    show_volumes: bool,
    apply_filter: str,
    ignore: str,
):
    """TODO(me) better description"""

    if out != "RICH":
        provider = route(url)
        manga = prepare_manga(provider.fetch_sync(), apply_filter, ignore)
        serializer = Serializer(manga)

        if out == "JSON":
            print(serializer.json(indent=4, chapters=chapters, pages=pages))
        elif out == "TOML":
            print(serializer.toml(chapters=chapters, pages=pages))
        elif out == "YAML":
            print(serializer.yaml(chapters=chapters, pages=pages))

    else:
        console = Console()
        with console.status("Fetching info", spinner="bouncingBar", spinner_style=""):
            provider = route(url)
            manga = prepare_manga(provider.fetch_sync(), apply_filter, ignore, True)

        console.print(
            rich_chapters(manga, show_urls, show_volumes)
            if chapters
            else rich_info(manga, show_urls)
        )
