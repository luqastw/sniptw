"""Link management commands."""

from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from cli.sniptw.client import APIError, get_client
from cli.sniptw.config import get_api_url, is_authenticated

app = typer.Typer(help="Link management commands")
console = Console()


def require_auth() -> None:
    """Check if user is authenticated."""
    if not is_authenticated():
        console.print("[bold red]Error:[/] You must be logged in to use this command.")
        console.print("Use [cyan]sniptw auth login[/] to login.")
        raise typer.Exit(1)


def format_datetime(dt_str: str | None) -> str:
    """Format datetime string for display."""
    if not dt_str:
        return "-"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except ValueError, AttributeError:
        return dt_str


@app.command("create")
def create_link(
    url: str = typer.Argument(..., help="The URL to shorten"),
    slug: str = typer.Option(None, "--slug", "-s", help="Custom slug (optional)"),
    expires: int = typer.Option(None, "--expires", "-e", help="Days until expiration"),
    password: str = typer.Option(
        None, "--password", "-p", help="Password protect the link"
    ),
) -> None:
    """Create a new short link."""
    require_auth()

    client = get_client()
    data: dict = {"original_url": url}

    if slug:
        data["slug"] = slug
    if expires:
        data["expires_in_days"] = expires
    if password:
        data["password"] = password

    with console.status("[bold green]Creating link...[/]"):
        try:
            response = client.post("/api/v1/links/", data=data, authenticated=True)

            short_url = f"{get_api_url()}/{response['slug']}"

            console.print(
                Panel(
                    f"[bold green]Link created successfully![/]\n\n"
                    f"[bold]Short URL:[/] [cyan]{short_url}[/]\n"
                    f"[bold]Slug:[/] {response['slug']}\n"
                    f"[bold]Original:[/] {response['original_url']}\n"
                    f"[bold]Expires:[/] {format_datetime(response.get('expires_at'))}",
                    title="New Link",
                    border_style="green",
                )
            )
        except APIError as e:
            console.print(f"[bold red]Failed to create link:[/] {e.message}")
            raise typer.Exit(1)


@app.command("list")
def list_links() -> None:
    """List all your links."""
    require_auth()

    client = get_client()

    with console.status("[bold green]Fetching links...[/]"):
        try:
            links = client.get("/api/v1/links/", authenticated=True)
        except APIError as e:
            console.print(f"[bold red]Failed to fetch links:[/] {e.message}")
            raise typer.Exit(1)

    if not links:
        console.print("[yellow]You don't have any links yet.[/]")
        console.print("Create one with [cyan]sniptw links create <url>[/]")
        return

    table = Table(title="Your Links", show_header=True, header_style="bold cyan")
    table.add_column("Slug", style="cyan")
    table.add_column("Original URL", max_width=50, overflow="ellipsis")
    table.add_column("Clicks", justify="right", style="green")
    table.add_column("Status", justify="center")
    table.add_column("Created", justify="right")
    table.add_column("Expires", justify="right")

    for link in links:
        status = "[green]Active[/]" if link["is_active"] else "[red]Inactive[/]"
        table.add_row(
            link["slug"],
            link["original_url"],
            str(link["click_count"]),
            status,
            format_datetime(link["created_at"]),
            format_datetime(link.get("expires_at")),
        )

    console.print(table)


@app.command("get")
def get_link(
    slug: str = typer.Argument(..., help="The slug of the link"),
) -> None:
    """Get details of a specific link."""
    client = get_client()

    with console.status("[bold green]Fetching link...[/]"):
        try:
            link = client.get(f"/api/v1/links/{slug}")
        except APIError as e:
            console.print(f"[bold red]Failed to fetch link:[/] {e.message}")
            raise typer.Exit(1)

    short_url = f"{get_api_url()}/{link['slug']}"
    status = "[green]Active[/]" if link["is_active"] else "[red]Inactive[/]"

    console.print(
        Panel(
            f"[bold]Short URL:[/] [cyan]{short_url}[/]\n"
            f"[bold]Slug:[/] {link['slug']}\n"
            f"[bold]Original:[/] {link['original_url']}\n"
            f"[bold]Clicks:[/] {link['click_count']}\n"
            f"[bold]Status:[/] {status}\n"
            f"[bold]Created:[/] {format_datetime(link['created_at'])}\n"
            f"[bold]Expires:[/] {format_datetime(link.get('expires_at'))}",
            title=f"Link: {link['slug']}",
            border_style="cyan",
        )
    )


@app.command("update")
def update_link(
    slug: str = typer.Argument(..., help="The slug of the link to update"),
    url: str = typer.Option(None, "--url", "-u", help="New original URL"),
    active: bool = typer.Option(
        None, "--active/--inactive", help="Set link active/inactive"
    ),
) -> None:
    """Update a link."""
    require_auth()

    if url is None and active is None:
        console.print("[yellow]No changes specified.[/]")
        console.print(
            "Use --url to change the URL or --active/--inactive to change status."
        )
        raise typer.Exit(1)

    client = get_client()
    data: dict = {}

    if url is not None:
        data["original_url"] = url
    if active is not None:
        data["is_active"] = active

    with console.status("[bold green]Updating link...[/]"):
        try:
            response = client.patch(
                f"/api/v1/links/{slug}", data=data, authenticated=True
            )
            console.print(f"[green]Link [cyan]{slug}[/] updated successfully![/]")

            if url:
                console.print(f"  [bold]New URL:[/] {response['original_url']}")
            if active is not None:
                status = (
                    "[green]Active[/]" if response["is_active"] else "[red]Inactive[/]"
                )
                console.print(f"  [bold]Status:[/] {status}")
        except APIError as e:
            console.print(f"[bold red]Failed to update link:[/] {e.message}")
            raise typer.Exit(1)


@app.command("delete")
def delete_link(
    slug: str = typer.Argument(..., help="The slug of the link to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a link."""
    require_auth()

    if not force:
        confirm = typer.confirm(f"Are you sure you want to delete link '{slug}'?")
        if not confirm:
            console.print("[yellow]Cancelled.[/]")
            raise typer.Exit()

    client = get_client()

    with console.status("[bold green]Deleting link...[/]"):
        try:
            client.delete(f"/api/v1/links/{slug}", authenticated=True)
            console.print(f"[green]Link [cyan]{slug}[/] deleted successfully![/]")
        except APIError as e:
            console.print(f"[bold red]Failed to delete link:[/] {e.message}")
            raise typer.Exit(1)


@app.command("shorten")
def quick_shorten(
    url: str = typer.Argument(..., help="The URL to shorten"),
) -> None:
    """Quickly shorten a URL (alias for create)."""
    require_auth()

    client = get_client()

    with console.status("[bold green]Shortening URL...[/]"):
        try:
            response = client.post(
                "/api/v1/links/",
                data={"original_url": url},
                authenticated=True,
            )
            short_url = f"{get_api_url()}/{response['slug']}"
            console.print(f"[bold cyan]{short_url}[/]")
        except APIError as e:
            console.print(f"[bold red]Error:[/] {e.message}")
            raise typer.Exit(1)
