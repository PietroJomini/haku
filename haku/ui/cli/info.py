import click
from rich import box
from rich.console import Console
from rich.table import Column, Table

from haku.meta import Manga
from haku.provider import route


def manga2table(manga: Manga, display_url: bool):
    """Transpose manga chapters into a rich table"""

    table = Table(
        Column("Index", justify="right"),
        Column("Title"),
        title=manga.title,
        box=box.ROUNDED,
    )

    if display_url:
        table.add_column("Url", overflow="fold")

    for chapter in manga.chapters:
        if display_url:
            table.add_row(chapter.index, chapter.title, chapter.url)
        else:
            table.add_row(chapter.index, chapter.title)

    return table


def info2table(manga, display_url):
    """Transpose manga info to a table"""

    table = Table("Key", "Value", box=box.ROUNDED)

    table.add_row("Title", manga.title)

    if display_url:
        table.add_row("Url", manga.url)

    if display_url and manga.cover_url is not None:
        table.add_row("Cover url", manga.cover_url)

    return table


@click.command()
@click.argument("url")
@click.option("-u", "--display-url", is_flag=True, help="Display chapters url")
@click.option("-m", "--manga-meta", is_flag=True, help="Display manga meta")
def info(url: str, display_url: bool, manga_meta: bool):
    """TODO(me) better description"""

    console = Console()

    provider = route(url)

    with console.status("Fetching info", spinner="bouncingBar", spinner_style=""):
        manga = provider.fetch_sync()

    table = (
        info2table(manga, display_url)
        if manga_meta
        else manga2table(manga, display_url)
    )

    console.print(table)
