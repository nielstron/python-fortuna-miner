from pathlib import Path

import click

from src.utils.keys import get_or_create_address


@click.command()
@click.argument("name")
def main(name):
    """
    Creates a testnet signing key, verification key, and address.
    """
    get_or_create_address(name)


if __name__ == "__main__":
    main()
