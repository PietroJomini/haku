import click


@click.command()
@click.argument("url")
def info(url: str):
    """TODO(me) better description"""
