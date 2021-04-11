from multiprocessing import Manager
from pathlib import Path
from typing import Optional, Pattern, Tuple

import click

from haku.exceptions import NoProviderFound
from haku.export.pdf import Pdf
from haku.meta import Manga
from haku.provider import Scraper, route
from haku.raw.downloader import Downloader, Method
from haku.raw.fs import Dotman, FTree, Reader
from haku.shelf import Filter, Shelf
from haku.utils.cli import Console
from haku.utils.cli.progress import Loader, Progress
from haku.utils.cli.renderable import Align, Text
from haku.utils.cli.table import Table


def fetch(
    console: Console,
    url: str,
    re: Optional[Pattern],
    filters: Optional[Filter],
    ignore: Optional[Filter],
    pages: bool,
) -> Optional[Tuple[Shelf, Scraper]]:
    """Check if `url` is routable as a provider or is a `.haku` file,
    then try to fetch manga info"""

    with Loader(console, "Fetching info"):

        # merge filters
        filters = filters or Filter.true()
        ignore = ignore or Filter.false()
        merged_filters = filters & ~ignore

        # fetch from url
        try:
            scraper = route(url)
            shelf = scraper.fetch_sync(merged_filters, fetch_pages=pages)
            return shelf, scraper
        except NoProviderFound:
            pass

        # fetch from file
        path = Path(url).resolve()
        if path.exists() and path.is_file() and path.suffix == ".haku":
            manga = Dotman(path.parent, name=path.name).read()
            scraper = route(manga.url)

            if scraper.provider.force_fetch:
                return scraper.fetch_sync(merged_filters, fetch_pages=pages), scraper

            return Shelf(manga).filter(merged_filters), scraper

        # TODO(me) handle url not recognised
        return None, None


def update(shelf: Shelf, editor: str) -> Shelf:
    """Open data in `editor` and update shelf"""

    content = shelf.manga.yaml()
    out = click.edit(content, editor=editor, require_save=False, extension=".yaml")
    updated_manga = Manga.from_yaml(out)
    return Shelf(updated_manga)


def display_info(console: Console, shelf: Shelf, show_chapters: bool):
    """Display manga info in a table"""

    manga = shelf.manga
    table = Table()

    # add basic meta
    info = Table()
    table.add_row(Text("META", expand=True, align=Align.center))
    info.add_column(Text("Title"), Text("Url"), Text("Cover"), same_width=True)
    info.add_column(manga.title, manga.url, manga.cover)
    table += info

    # add chapters
    if show_chapters:
        columns = [
            [Text("Volume")],
            [Text("Index")],
            [Text("Title")],
            [Text("Url", expand=True)],
        ]
        for chapter in manga.chapters:
            columns[0].append(
                Text(f"{chapter.volume:g}" if chapter.volume is not None else "")
            )
            columns[1].append(Text(f"{chapter.index:g}"))
            columns[2].append(Text(chapter.title or ""))
            columns[3].append(chapter.url)

        table.add_row(Text("CHAPTERS", expand=True, align=Align.center))

        chapters = Table()
        chapters.add_column(*columns[0], same_width=True)
        chapters.add_column(*columns[1], same_width=True)
        chapters.add_column(*columns[2], same_width=True)
        chapters.add_column(*columns[3])

        table = table + chapters

    console.print(table)


def export_dotfile(out: Path, shelf: Shelf):
    """Export .haku file to out"""

    manager = Dotman(out, name=f"{shelf.manga.title}.haku")
    manager.dump(shelf.manga)


def download(
    console: Console,
    out: Path,
    shelf: Shelf,
    scraper: Scraper,
    batch_size: int,
    rate_limit: int,
) -> FTree:
    """Check for already existent data and download missing"""

    # check for missinng data
    tree = FTree(out, shelf.manga)
    reader = Reader(tree)
    missing = reader.missing()

    n_pages = sum((len(chapter.pages) for chapter in missing.chapters)) + 1
    with Progress(console, n_pages, description="Dowloading...") as bar:
        downloader = Downloader(scraper, missing, tree)
        downloader.endpoints.on("page.end", lambda *_: bar(1))

        return downloader.download(Method.batch(batch_size), rate_limit=rate_limit)


def convert_pdf(
    console: Console,
    src: FTree,
    shelf: Shelf,
    destination: Path,
    merge: Optional[str],
):
    """Convert to pdf"""

    with Progress(
        console,
        len(shelf.manga.chapters),
        description="Converting...",
    ) as bar:

        manager = Manager()
        shared_dict = manager.dict()
        shared_dict["tot"] = 0

        def update(c):
            if c.title not in shared_dict:
                shared_dict["tot"] += 1
                bar.to(shared_dict["tot"])

            shared_dict[c.title] = 0

        # TODO(me) move the splitting process to FTree
        # TODO(me) investigate progress overflow
        # TODO(me) use the same process pool for each chunk
        #          -> two pools, one that convert and one that merge?
        merge_tree = FTree(destination, shelf.manga)
        destination = destination if merge is None else src

        if merge == "volume":
            volumes = shelf.split_volumes()
            chunks = [(volumes[volume], f"{volume:g}", True) for volume in volumes]
        elif merge == "manga":
            chunks = [(shelf.manga.chapters, shelf.manga.title, True)]
            merge_tree.root = merge_tree.root.parent
        else:
            chunks = [(shelf.manga.chapters, shelf.manga.title, False)]

        for chapters, title, merge in chunks:
            manga = Manga("", title, None, chapters)
            pdf = Pdf(manga, src, destination, merge, merge_tree)
            pdf.on("chapter.end", update)
            pdf.convert()
