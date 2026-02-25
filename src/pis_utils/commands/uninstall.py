"""Uninstall command group."""

import typer

from pis_utils.commands import conda, vscode

app = typer.Typer(help="Uninstall tools and applications")

# Register subcommands
app.command(name="vscode")(vscode.uninstall)
app.command(name="conda")(conda.uninstall)
