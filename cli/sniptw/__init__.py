"""sniptw CLI - A command line interface for the sniptw URL shortener."""

import typer
from rich.console import Console
from rich.panel import Panel

from cli.sniptw.commands import analytics, auth, links
from cli.sniptw.config import get_api_url, set_api_url

app = typer.Typer(
    name="sniptw",
    help="A fast and simple URL shortener CLI",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
console = Console()

# Register command groups
app.add_typer(
    auth.app, name="auth", help="Authentication commands (login, register, logout)"
)
app.add_typer(
    links.app, name="links", help="Link management (create, list, update, delete)"
)
app.add_typer(
    analytics.app, name="analytics", help="View link statistics and analytics"
)


@app.command()
def shorten(
    url: str = typer.Argument(..., help="The URL to shorten"),
) -> None:
    """Quickly shorten a URL."""
    links.quick_shorten(url)


@app.command()
def config(
    api_url: str = typer.Option(None, "--api-url", "-a", help="Set the API base URL"),
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
) -> None:
    """Configure CLI settings."""
    if show or api_url is None:
        console.print(
            Panel(
                f"[bold]API URL:[/] [cyan]{get_api_url()}[/]",
                title="Current Configuration",
                border_style="cyan",
            )
        )

    if api_url:
        set_api_url(api_url)
        console.print(f"[green]API URL set to:[/] [cyan]{api_url}[/]")


@app.command()
def version() -> None:
    """Show the CLI version."""
    console.print("[bold cyan]sniptw[/] version [green]0.1.0[/]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
