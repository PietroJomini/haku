import click

from haku.ui.cli.download import download
from haku.ui.cli.info import info


@click.group()
def main():
    """TODO(me) better description"""


main.add_command(info)
main.add_command(download)
