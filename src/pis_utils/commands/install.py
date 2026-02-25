"""Install command group."""

import typer

from pis_utils.commands import conda, vscode

app = typer.Typer(help="Install various tools and applications")

# Register subcommands
app.command(name="vscode")(vscode.install)
app.command(name="conda")(conda.install)
