import click

from haku.ui.cli.download import download
from haku.ui.cli.info import info

context_settings = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=context_settings)
def main():
    """TODO(me) better description"""


main.add_command(info)
main.add_command(download)
