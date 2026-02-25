"""Main CLI application."""

import typer

from pis_utils import __version__
from pis_utils.commands import install, uninstall

app = typer.Typer(
    name="pis-utils",
    help="Cross-platform Python installation support scripts for DTU",
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"pis-utils version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """Cross-platform Python installation support scripts for DTU."""


# Register command groups
app.add_typer(install.app, name="install")
app.add_typer(uninstall.app, name="uninstall")


if __name__ == "__main__":
    app()
