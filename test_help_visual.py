#!/usr/bin/env python3
"""Visual test for help overlay - shows sample rendering."""

from claude_multi_terminal.help.help_overlay import HelpOverlay, HelpCategory
from claude_multi_terminal.types import AppMode
from rich.console import Console
from rich.text import Text
from claude_multi_terminal.theme import theme, boxes

console = Console()

def test_help_content():
    """Test help content rendering."""
    overlay = HelpOverlay(current_mode=AppMode.NORMAL)

    console.print("\n[bold cyan]╔═══════════════════════════════════════════════════════════╗[/]")
    console.print("[bold cyan]║[/]  [bold red]HELP - Claude Multi-Terminal[/]                             [bold cyan]║[/]")
    console.print("[bold cyan]║[/]  Current Mode: NORMAL | Press ? to close                  [bold cyan]║[/]")
    console.print("[bold cyan]╠═══════════════════════════════════════════════════════════╣[/]")
    console.print("[bold cyan]║[/]                                                            [bold cyan]║[/]")

    # Sample entries from each category
    console.print("[bold cyan]║[/]  [bold red]GENERAL COMMANDS[/]                                          [bold cyan]║[/]")
    console.print("[bold cyan]║[/]  [dim cyan]────────────────────────────────────────────────────[/]     [bold cyan]║[/]")

    general_entries = [e for e in overlay.help_entries if e.category == HelpCategory.GENERAL][:4]
    for entry in general_entries:
        console.print(f"[bold cyan]║[/]  [bold white]{entry.key:15}[/] {entry.description[:40]:40} [bold cyan]║[/]")

    console.print("[bold cyan]║[/]                                                            [bold cyan]║[/]")
    console.print("[bold cyan]║[/]  [bold red]WORKSPACE MANAGEMENT (1-9)[/]                                [bold cyan]║[/]")
    console.print("[bold cyan]║[/]  [dim cyan]────────────────────────────────────────────────────[/]     [bold cyan]║[/]")

    workspace_entries = [e for e in overlay.help_entries if e.category == HelpCategory.WORKSPACE][:3]
    for entry in workspace_entries:
        console.print(f"[bold cyan]║[/]  [bold white]{entry.key:15}[/] {entry.description[:40]:40} [bold cyan]║[/]")

    console.print("[bold cyan]║[/]                                                            [bold cyan]║[/]")
    console.print("[bold cyan]║[/]  [dim]Use j/k to scroll, Tab for categories, ? or Esc to close[/] [bold cyan]║[/]")
    console.print("[bold cyan]╚═══════════════════════════════════════════════════════════╝[/]\n")

def test_category_counts():
    """Show category distribution."""
    overlay = HelpOverlay()

    console.print("\n[bold yellow]Help Entry Distribution:[/]\n")

    total = len(overlay.help_entries)
    console.print(f"Total entries: [bold green]{total}[/]\n")

    console.print("[bold]By Category:[/]")
    for category in HelpCategory:
        entries = [e for e in overlay.help_entries if e.category == category]
        bar = "█" * len(entries)
        console.print(f"  {category.value:15} [{len(entries):2}] {bar}")

    console.print("\n[bold]By Mode:[/]")
    for mode in AppMode:
        entries = [e for e in overlay.help_entries if e.mode == mode]
        bar = "█" * (len(entries) // 2)
        console.print(f"  {mode.value:10} [{len(entries):2}] {bar}")

if __name__ == "__main__":
    console.print("\n[bold green]═══ Help Overlay Visual Test ═══[/]\n")
    test_help_content()
    test_category_counts()
    console.print("\n[bold green]✓ Visual test complete![/]\n")
