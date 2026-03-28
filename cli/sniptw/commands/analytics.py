"""Analytics commands."""

from datetime import datetime

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cli.sniptw.client import APIError, get_client
from cli.sniptw.config import is_authenticated

app = typer.Typer(help="Analytics and statistics commands")
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
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError, AttributeError:
        return dt_str


@app.command("stats")
def link_stats(
    slug: str = typer.Argument(..., help="The slug of the link"),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Number of recent clicks to show"
    ),
) -> None:
    """Get detailed statistics for a link."""
    require_auth()

    client = get_client()

    with console.status("[bold green]Fetching analytics...[/]"):
        try:
            stats = client.get(f"/api/v1/analytics/{slug}", authenticated=True)
        except APIError as e:
            console.print(f"[bold red]Failed to fetch analytics:[/] {e.message}")
            raise typer.Exit(1)

    # Summary panel
    console.print(
        Panel(
            f"[bold]Slug:[/] [cyan]{stats['slug']}[/]\n"
            f"[bold]Original URL:[/] {stats['original_url']}\n"
            f"[bold]Total Clicks:[/] [green]{stats['total_clicks']}[/]",
            title="Link Statistics",
            border_style="cyan",
        )
    )

    clicks = stats.get("clicks", [])
    if not clicks:
        console.print("\n[yellow]No clicks recorded yet.[/]")
        return

    # Click details table
    console.print(
        f"\n[bold]Recent Clicks[/] (showing {min(limit, len(clicks))} of {len(clicks)}):\n"
    )

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Time", style="dim")
    table.add_column("Country")
    table.add_column("Device")
    table.add_column("Referer", max_width=40, overflow="ellipsis")

    for click in clicks[:limit]:
        table.add_row(
            format_datetime(click.get("clicked_at")),
            click.get("country") or "Unknown",
            click.get("device_type") or "Unknown",
            click.get("referer") or "Direct",
        )

    console.print(table)

    # Quick stats
    if clicks:
        countries = {}
        devices = {}
        for click in clicks:
            country = click.get("country") or "Unknown"
            device = click.get("device_type") or "Unknown"
            countries[country] = countries.get(country, 0) + 1
            devices[device] = devices.get(device, 0) + 1

        console.print("\n[bold]Top Countries:[/]")
        for country, count in sorted(
            countries.items(), key=lambda x: x[1], reverse=True
        )[:5]:
            bar_len = int((count / len(clicks)) * 20)
            bar = "[green]" + "█" * bar_len + "[/]" + "░" * (20 - bar_len)
            console.print(f"  {country:15} {bar} {count}")

        console.print("\n[bold]Devices:[/]")
        for device, count in sorted(devices.items(), key=lambda x: x[1], reverse=True):
            bar_len = int((count / len(clicks)) * 20)
            bar = "[blue]" + "█" * bar_len + "[/]" + "░" * (20 - bar_len)
            console.print(f"  {device:15} {bar} {count}")


@app.command("summary")
def summary() -> None:
    """Show a summary of all your links and their clicks."""
    require_auth()

    client = get_client()

    with console.status("[bold green]Fetching data...[/]"):
        try:
            links = client.get("/api/v1/links/", authenticated=True)
        except APIError as e:
            console.print(f"[bold red]Failed to fetch data:[/] {e.message}")
            raise typer.Exit(1)

    if not links:
        console.print("[yellow]You don't have any links yet.[/]")
        return

    total_links = len(links)
    active_links = sum(1 for link in links if link["is_active"])
    total_clicks = sum(link["click_count"] for link in links)

    # Summary panel
    console.print(
        Panel(
            f"[bold]Total Links:[/] {total_links}\n"
            f"[bold]Active Links:[/] [green]{active_links}[/]\n"
            f"[bold]Inactive Links:[/] [yellow]{total_links - active_links}[/]\n"
            f"[bold]Total Clicks:[/] [cyan]{total_clicks}[/]",
            title="Account Summary",
            border_style="cyan",
        )
    )

    # Top performing links
    if links:
        console.print("\n[bold]Top Performing Links:[/]\n")
        sorted_links = sorted(links, key=lambda x: x["click_count"], reverse=True)[:5]

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Slug", style="cyan")
        table.add_column("Clicks", justify="right", style="green")
        table.add_column("URL", max_width=50, overflow="ellipsis")

        for link in sorted_links:
            table.add_row(
                link["slug"],
                str(link["click_count"]),
                link["original_url"],
            )

        console.print(table)
