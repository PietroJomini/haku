from pathlib import Path

import click


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
    filters: str,
    ignore: str,
    re: str,
):
    """TODO(me) better description"""
