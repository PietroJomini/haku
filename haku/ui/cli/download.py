from pathlib import Path

import click
from rich.console import Console
from rich.progress import BarColumn, Progress, TimeElapsedColumn, TimeRemainingColumn

from haku.provider import Scraper
from haku.raw.downloader import Downloader, Method
from haku.shelf import Shelf
from haku.ui.cli.common import rich_fetch


def rich_download(
    shelf: Shelf,
    scraper: Scraper,
    path: Path,
    batch_size: int,
    rate_limit: int,
):
    """Download manga with a rich trackbar"""

    downloader = Downloader(scraper, shelf, path)
    n_pages = sum((len(chapter.pages) for chapter in shelf.manga.chapters)) + 1

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        "[",
        TimeElapsedColumn(),
        "/",
        TimeRemainingColumn(),
        "]",
    ) as track:
        dl_task = track.add_task("Downloading...", total=n_pages)
        downloader.endpoints.on("page.end", lambda *_: track.update(dl_task, advance=1))

        downloader.download(Method.batch(batch_size), rate_limit=rate_limit)


@click.command()
@click.argument("url")
@click.option(
    "-p",
    "--path",
    default=lambda: Path.cwd(),
    help="Output folder",
    show_default=".",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
)
@click.option(
    "-o",
    "--out",
    default="RAW",
    type=click.Choice(["RAW", "PDF"], case_sensitive=False),
    help="Output format",
    show_default=True,
)
@click.option(
    "-s",
    "--batch-size",
    default=0,
    type=int,
    help="Download batch size",
    show_default=True,
)
@click.option(
    "-r",
    "--rate-limit",
    default=200,
    type=int,
    help="Limit of concurrent connections",
    show_default=True,
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
def download(
    url: str,
    path: str,
    out: str,
    batch_size: int,
    rate_limit: int,
    apply_filter: str,
    ignore: str,
    re: str,
):
    """TODO(me) better description"""

    shelf, scraper = rich_fetch(Console(), url, re, apply_filter, ignore, True)
    rich_download(shelf, scraper, path, batch_size, rate_limit)
