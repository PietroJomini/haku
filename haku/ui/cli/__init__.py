from pathlib import Path

import click


@click.command()
@click.argument("url")
@click.option(
    "--info",
    "-i",
    is_flag=True,
    help="show info about the manga without downloading it",
)
@click.option(
    "--path",
    "-p",
    default=lambda: Path.cwd(),
    help="where to save the downloaded manga",
    show_default="current path",
    type=click.Path(exists=True, file_okay=False, writable=True, resolve_path=True),
)
@click.option(
    "--out",
    "-o",
    default="RAW",
    type=click.Choice(["RAW", "PDF"], case_sensitive=False),
    help="saved manga format",
    show_default=True,
)
@click.option(
    "--batch-size",
    "-s",
    default=0,
    type=int,
    help="size of the downloaded batches",
    show_default=True,
)
def main(url: str, info: bool, path: str, out: str, batch_size: int):
    """Haku manga downloader"""

    print(url)
    print(path)
    print(out)
    print(batch_size)
