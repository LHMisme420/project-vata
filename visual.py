from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import BarColumn, Progress, TextColumn
from rich.theme import Theme

# Custom 2026 Cyberpunk Theme
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "danger": "bold red",
    "success": "bold green"
})

console = Console(theme=custom_theme)

def display_dashboard(stats, soul_score, seal_art):
    """Renders the VATA Security Dashboard."""
    
    # 1. Header Table
    table = Table(title="🛡️ PROJECT VATA: INTEGRITY MONITOR", style="cyan")
    table.add_column("Metric", style="white")
    table.add_column("Value", justify="right")
    
    table.add_row("Logic Nodes", str(stats.get('nodes', 0)))
    table.add_row("Complexity Index", str(stats.get('complexity', 0)))
    table.add_row("Status", "[bold green]VERIFIED[/bold green]")
    
    # 2. Progress Bar for Soul Score
    console.print(table)
    console.print(f"\n[bold]Humanity Alignment (Soul Score):[/bold]")
    
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        "[progress.percentage]{task.percentage:>3.0f}%",
    ) as progress:
        task = progress.add_task("[cyan]Soul Scan...", total=100)
        progress.update(task, completed=soul_score)

    # 3. The Seal Panel
    console.print(Panel(seal_art, title="[bold white]AUTHENTICITY SEAL[/bold white]", border_style="green"))
