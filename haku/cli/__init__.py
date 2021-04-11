import os
from pathlib import Path
from typing import Optional, Pattern

import click
import cloup

from haku.cli.controllers import (
    convert_pdf,
    display_info,
    download,
    export_dotfile,
    fetch,
    update,
)
from haku.cli.types import EditorType, FilterType, ReType
from haku.shelf import Filter
from haku.utils import tmpdir
from haku.utils.cli import Console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
C_WIDTH = 100


@cloup.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url")
@cloup.option_group(
    "Basic usage",
    cloup.option(
        "-o",
        "--out",
        type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
        default=Path.cwd(),
        show_default=".",
    ),
    cloup.option(
        "-c",
        "--convert",
        type=click.Choice(["pdf"], case_sensitive=False),
    ),
    cloup.option(
        "-m",
        "--merge",
        type=click.Choice(["volume", "manga"], case_sensitive=False),
    ),
    cloup.option("-y", "--yes", is_flag=True),
)
@cloup.option_group(
    "Meta",
    cloup.option("-i", "--info", is_flag=True),
    cloup.option("-C", "--show-chapters", is_flag=True),
    cloup.option("-e", "--export", is_flag=True),
)
@cloup.option_group(
    "Filters",
    cloup.option("-f", "--filter", "filters", type=FilterType()),
    cloup.option("--ignore", type=FilterType()),
    cloup.option("-v", "--override-volumes", default=""),
)
@cloup.option_group(
    "Fetch / Download",
    cloup.option("-r", "--re", type=ReType("index")),
    cloup.option("--batch-size", type=int, default=100, show_default=True),
    cloup.option("--rate-limit", type=int, default=100, show_default=True),
)
@cloup.option_group(
    "Editor",
    cloup.option(
        "-E",
        "--editor",
        type=EditorType(),
        default=lambda: os.environ.get("EDITOR", ""),
        show_default="$EDITOR",
    ),
)
def main(
    url: str,
    out: str,
    convert: Optional[str],
    merge: Optional[str],
    yes: bool,
    info: bool,
    export: bool,
    filters: Optional[Filter],
    ignore: Optional[Filter],
    re: Optional[Pattern],
    batch_size: int,
    rate_limit: int,
    editor: str,
    show_chapters: bool,
    override_volumes: str,
):
    """Haku cli"""

    out = Path(out)
    shelf, scraper = fetch(Console(columns=C_WIDTH), url, re, filters, ignore, not info)

    shelf.override_volumes(override_volumes)
    shelf = shelf if yes else update(shelf, editor)

    if info:
        display_info(Console(), shelf, show_chapters)
        return

    if export:
        export_dotfile(out, shelf)
        return

    tree = download(
        Console(columns=C_WIDTH),
        out if convert is None else tmpdir(),
        shelf,
        scraper,
        batch_size,
        rate_limit,
    )

    if convert == "pdf":
        convert_pdf(Console(columns=C_WIDTH), tree, shelf, out, merge)
