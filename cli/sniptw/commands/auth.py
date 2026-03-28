"""Authentication commands."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from cli.sniptw.client import APIError, get_client
from cli.sniptw.config import clear_token, get_token, is_authenticated, save_token

app = typer.Typer(help="Authentication commands")
console = Console()


@app.command()
def login(
    username: str = typer.Option(None, "--username", "-u", help="Email or username"),
    password: str = typer.Option(None, "--password", "-p", help="Password"),
) -> None:
    """Login to sniptw and save access token."""
    if is_authenticated():
        if not typer.confirm("You are already logged in. Do you want to re-login?"):
            raise typer.Exit()

    # Prompt for credentials if not provided
    if not username:
        username = Prompt.ask("[bold cyan]Email[/]")
    if not password:
        password = Prompt.ask("[bold cyan]Password[/]", password=True)

    client = get_client()

    with console.status("[bold green]Authenticating...[/]"):
        try:
            response = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": password},
                form_data=True,
            )
            save_token(response["access_token"])
            console.print(
                Panel("[bold green]Login successful![/]", border_style="green")
            )
        except APIError as e:
            console.print(f"[bold red]Login failed:[/] {e.message}")
            raise typer.Exit(1)


@app.command()
def register(
    email: str = typer.Option(None, "--email", "-e", help="Email address"),
    username: str = typer.Option(None, "--username", "-u", help="Username"),
    password: str = typer.Option(None, "--password", "-p", help="Password"),
) -> None:
    """Register a new account."""
    # Prompt for details if not provided
    if not email:
        email = Prompt.ask("[bold cyan]Email[/]")
    if not username:
        username = Prompt.ask("[bold cyan]Username[/]")
    if not password:
        password = Prompt.ask("[bold cyan]Password[/]", password=True)
        password_confirm = Prompt.ask("[bold cyan]Confirm password[/]", password=True)
        if password != password_confirm:
            console.print("[bold red]Passwords do not match![/]")
            raise typer.Exit(1)

    client = get_client()

    with console.status("[bold green]Creating account...[/]"):
        try:
            client.post(
                "/api/v1/auth/register",
                data={"email": email, "username": username, "password": password},
            )
            console.print(
                Panel(
                    "[bold green]Account created successfully![/]\n"
                    "You can now login with [cyan]sniptw auth login[/]",
                    border_style="green",
                )
            )
        except APIError as e:
            console.print(f"[bold red]Registration failed:[/] {e.message}")
            raise typer.Exit(1)


@app.command()
def logout() -> None:
    """Logout and clear stored credentials."""
    if not is_authenticated():
        console.print("[yellow]You are not logged in.[/]")
        raise typer.Exit()

    clear_token()
    console.print("[green]Logged out successfully.[/]")


@app.command()
def status() -> None:
    """Check authentication status."""
    if is_authenticated():
        token = get_token()
        # Show truncated token for security
        if token:
            masked = f"{token[:10]}...{token[-10:]}"
            console.print(f"[green]Authenticated[/] (token: {masked})")
    else:
        console.print(
            "[yellow]Not authenticated.[/] Use [cyan]sniptw auth login[/] to login."
        )
