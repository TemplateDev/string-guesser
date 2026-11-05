from collections.abc import Callable
import string
import time
from argparse import ArgumentParser

CHARSET = tuple(
    character
    for group in (
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        string.punctuation,
        string.whitespace,
    )
    for character in group
)

secret: str = ""

def run_solver(
        iterations: int = 10_000,
        steps: int = 1000,
        target_score: float = 1.0,
        on_iteration: Callable[[int, str, float], None] | None = None
    ) -> tuple[str, float]:
    from lib import compare
    from algorithm import Solver
    
    def objective(given: str) -> float:
        return compare(given, secret) / 100.0
    
    solver = Solver(
        " " * len(secret),
        CHARSET,
        objective
    )

    return solver.run(
        iterations,
        steps,
        on_iteration,
        target_score
    )

def run_with_console(args) -> None:
    from rich.console import Console, Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.progress import (
        BarColumn,
        Progress,
        TaskProgressColumn,
        TimeElapsedColumn,
    )
    from rich.table import Table
    from rich.text import Text

    console = Console()
    progress = Progress(
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        expand=True,
        auto_refresh=False,
    )
    task_id = progress.add_task("Search", total=max(args.iterations, 0))

    def make_table(
        status: str,
        iteration: int,
        score: float | None,
    ) -> Table:
        table = Table(title="String Guess Solver", border_style="bright_blue")
        table.add_column("Status", style="cyan")
        table.add_column("Iteration", justify="right")
        table.add_column("Match", justify="right", style="green")
        table.add_column("Target", justify="right", style="yellow")
        table.add_row(
            status,
            f"{iteration:,}",
            "-" if score is None else f"{score:.2%}",
            f"{args.target_percentage:.1f}%",
        )
        return table

    def make_display(
        status: str,
        iteration: int,
        best: str,
        score: float | None,
    ) -> Group:
        return Group(
            make_table(status, iteration, score),
            progress,
            Panel(Text(repr(best), style="magenta"), title="Best string"),
        )

    latest_iteration = 0
    with Live(
        make_display("Starting", 0, "Waiting for first result...", None),
        console=console,
        refresh_per_second=10,
        transient=True,
    ) as live:
        def on_iteration(iteration: int, best: str, score: float) -> None:
            nonlocal latest_iteration
            latest_iteration = iteration
            progress.update(task_id, completed=iteration)
            live.update(make_display("Searching", iteration, best, score))
            if args.delay is not None and args.delay != 0:
                time.sleep(args.delay)

        best, score = run_solver(
            iterations=args.iterations,
            steps=args.steps,
            target_score=args.target_percentage / 100,
            on_iteration=on_iteration,
        )
    status = "Target reached" if score >= args.target_percentage / 100 else "Finished"
    console.print(
        Group(
            make_table(status, latest_iteration, score),
            Panel(Text(repr(best), style="magenta"), title="Best string"),
        )
    )

def main() -> None:
    parser = ArgumentParser(description="Find a string matching the secret.")
    parser.add_argument("secret", help="the secret string to match")
    parser.add_argument("--iterations", type=int, default=10_000, help="iteration count")
    parser.add_argument("--steps", type=int, default=1000, help="iteration steps")
    parser.add_argument(
        "--target-percentage",
        type=float,
        default=100.0,
        help="target match percentage (0-100)",
    )
    parser.add_argument("--delay", type=float, help="delay in seconds after each iteration")
    args = parser.parse_args()

    global secret
    secret = args.secret
    run_with_console(args)

if __name__ == "__main__":
    main()
