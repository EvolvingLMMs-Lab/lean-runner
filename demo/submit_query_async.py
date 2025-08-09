import asyncio
import logging
from pathlib import Path

from lean_runner import AsyncLeanClient
from lean_runner.proof.proto import LeanProofStatus, Proof, ProofResult
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table

logging.disable(logging.INFO)


def has_error(result: ProofResult) -> bool:
    """Check if a proof result has any error messages."""
    if result.result and "messages" in result.result:
        for msg in result.result["messages"]:
            if msg.get("severity") == "error":
                return True
    return False


def get_status_display(res: ProofResult) -> str:
    """Get the rich display string for a proof result status."""
    status = res.status.value
    if res.status == LeanProofStatus.RUNNING:
        return f"{Spinner('dots')} [yellow]{status}[/yellow]"
    elif res.status == LeanProofStatus.FINISHED:
        if has_error(res):
            return "[red]FAILED[/red] ❌"
        else:
            return "[green]PROVED[/green] 🎉"
    elif res.status == LeanProofStatus.ERROR:
        return "[red]ERROR[/red] ❌"
    else:  # PENDING
        return f"[yellow]{status}[/yellow]"


def generate_status_table(
    proof_map: dict[str, Proof], results_status: dict[str, ProofResult]
) -> Table:
    """Generate a table to display the status of proofs."""
    table = Table(title="Lean Proof Status")
    table.add_column("File", justify="left", style="cyan", no_wrap=True)
    table.add_column("UUID", justify="left", style="magenta")
    table.add_column("Status", justify="left")

    for fname, p_obj in proof_map.items():
        res = results_status.get(fname)
        status_text = "[bold yellow]PENDING[/bold yellow]"
        if res:
            status_text = get_status_display(res)
        table.add_row(fname, str(p_obj.id), status_text)
    return table


async def main():
    """Submit multiple proofs and display their status in a live table."""
    demo_dir = Path(__file__).parent
    lean_files = [
        demo_dir / "test1.lean",
        demo_dir / "test2.lean",
        demo_dir / "test3.lean",
        demo_dir / "test4.lean",
    ]

    async with AsyncLeanClient(base_url="http://0.0.0.0:8080", timeout=60.0) as client:
        submitted_proofs: list[Proof] = await asyncio.gather(
            *[client.submit(proof=file) for file in lean_files]
        )

        proof_map: dict[str, Proof] = {
            file.name: proof
            for file, proof in zip(lean_files, submitted_proofs, strict=False)
        }

        results_status: dict[str, ProofResult] = {}

        with Live(
            generate_status_table(proof_map, results_status),
            refresh_per_second=4,
            transient=True,
        ) as live:
            pending_proofs = list(proof_map.items())

            while pending_proofs:
                tasks = [client.get_result(proof=p) for _, p in pending_proofs]
                query_results: list[ProofResult] = await asyncio.gather(*tasks)

                newly_pending = []
                for (filename, proof), result in zip(
                    pending_proofs, query_results, strict=False
                ):
                    results_status[filename] = result
                    if result.status not in {
                        LeanProofStatus.FINISHED,
                        LeanProofStatus.ERROR,
                    }:
                        newly_pending.append((filename, proof))

                pending_proofs = newly_pending

                live.update(generate_status_table(proof_map, results_status))
                if not pending_proofs:
                    break
                await asyncio.sleep(1)

        console.print(generate_status_table(proof_map, results_status))

        console.print("\n[bold underline]Final Proof Results:[/bold underline]")
        for filename, result in results_status.items():
            panel_color = "green" if not has_error(result) else "red"
            console.print(
                Panel(
                    str(result),
                    title=f"[bold]{filename}[/bold]",
                    border_style=panel_color,
                    title_align="left",
                )
            )


if __name__ == "__main__":
    console = Console()
    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
