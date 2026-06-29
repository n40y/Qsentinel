# cli/progress.py

from rich.progress import (
    Progress,
    BarColumn,
    TimeRemainingColumn,
    TimeElapsedColumn,
    TextColumn,
    SpinnerColumn,
)
from rich.console import Console
from typing import Callable, Any


console = Console()

def run_with_progress(
    task_name: str,
    func: Callable[[], Any],
    description: str = "Exécution en cours...",
) -> Any:
    """
    Exécute une fonction avec une barre de progression.

    Args:
        task_name: Nom de la tâche (affiché dans la barre).
        func: Fonction à exécuter.
        description: Description supplémentaire.

    Returns:
        Résultat de la fonction.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"[cyan]{task_name}[/cyan]", total=None)
        progress.update(task, description=description)
        result = func()
        progress.update(task, completed=True, description=f"[green]✅ {task_name} terminé[/green]")
        return result
