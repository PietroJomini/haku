from multiprocessing import Manager
from pathlib import Path

import click
from rich.console import Console as RichConsole

from haku.export.pdf import Pdf
from haku.provider import Scraper
from haku.raw.downloader import Downloader, Method
from haku.raw.fs import FTree
from haku.shelf import Shelf
from haku.ui.cli.common import rich_fetch
from haku.utils import tmpdir
from haku.utils.cli import Console, Progress


def dl_progress(
    console: Console,
    shelf: Shelf,
    scraper: Scraper,
    path: Path,
    batch_size: int,
    rate_limit: int,
):
    """Download manga with a rich trackbar"""

    with Progress(
        console,
        sum((len(chapter.pages) for chapter in shelf.manga.chapters)) + 1,
        description="Downloading...",
    ) as bar:

        downloader = Downloader(scraper, shelf, path)
        downloader.endpoints.on("page.end", lambda *_: bar.advance(1))

        return downloader.download(Method.batch(batch_size), rate_limit=rate_limit)


def to_pdf(
    console: Console,
    src: FTree,
    shelf: Shelf,
    destination: str,
):
    """Convert to pdf"""

    with Progress(
        console,
        len(shelf.manga.chapters),
        "Converting...",
    ) as bar:

        manager = Manager()
        shared_dict = manager.dict()
        shared_dict["tot"] = 0

        def update(c):
            shared_dict["tot"] += 1
            bar.to(shared_dict["tot"])

        out_tree = FTree(destination, shelf.manga)
        pdf = Pdf(shelf, src, out_tree)
        pdf.on("chapter.end", update)
        pdf.convert()


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

    console = Console(columns=100)

    shelf, scraper = rich_fetch(RichConsole(), url, re, apply_filter, ignore, True)

    destination = tmpdir() if out != "RAW" else path
    tree = dl_progress(console, shelf, scraper, destination, batch_size, rate_limit)

    if out == "PDF":
        to_pdf(console, tree, shelf, path)
