from multiprocessing import Manager
from pathlib import Path

import click

from haku.cli.common import rich_fetch
from haku.export.pdf import Pdf
from haku.meta import Manga
from haku.provider import Scraper
from haku.raw.downloader import Downloader, Method
from haku.raw.fs import FTree
from haku.shelf import Shelf
from haku.utils import tmpdir
from haku.utils.cli import Console
from haku.utils.cli.progress import Progress


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
        downloader.endpoints.on("page.end", lambda *_: bar(1))

        return downloader.download(Method.batch(batch_size), rate_limit=rate_limit)


def to_pdf(
    console: Console,
    src: FTree,
    shelf: Shelf,
    destination: str,
    merge: bool,
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
        pdf = Pdf(
            shelf,
            src,
            out_tree if not merge else src,
            merge,
            out_tree.root.parent,
        )
        pdf.on("chapter.end", update)
        pdf.convert()


def to_pdf_volumes(
    console: Console,
    src: FTree,
    shelf: Shelf,
    destination: str,
    _: bool,
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
        volumes = shelf.split_volumes()

        for volume in volumes:
            manga = Manga("", f"{volume:g}", None, volumes[volume])
            pdf = Pdf(manga, src, src, True, out_tree)
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
    "-m",
    "--merge",
    is_flag=True,
    help="On formats that supports it, merge chapters",
)
@click.option(
    "--split-volumes",
    is_flag=True,
    help="On formats that supports it, merge chapters in volumes",
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
    merge: bool,
    split_volumes: bool,
    batch_size: int,
    rate_limit: int,
    apply_filter: str,
    ignore: str,
    re: str,
):
    """TODO(me) better description"""

    console = Console(columns=100)

    shelf, scraper = rich_fetch(console, url, re, apply_filter, ignore, True)
    tree = dl_progress(
        console,
        shelf,
        scraper,
        tmpdir() if out != "RAW" or merge else path,
        batch_size,
        rate_limit,
    )

    if out == "PDF":
        f = to_pdf_volumes if split_volumes else to_pdf
        f(console, tree, shelf, path, merge)
