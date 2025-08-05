import asyncio
import logging
from pathlib import Path
from typing import Dict, List

from lean_client import AsyncLeanClient
from lean_client.proof.proto import LeanProofStatus, Proof, ProofResult
from rich.console import Console
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table

logging.disable(logging.INFO)


def generate_table(proofs: Dict[str, ProofResult]) -> Table:
    """Generate a table to display the status of proofs."""
    table = Table(title="Lean Proof Status")
    table.add_column("File", justify="left", style="cyan", no_wrap=True)
    table.add_column("UUID", justify="left", style="magenta")
    table.add_column("Status", justify="left")

    for filename, proof_result in proofs.items():
        status = proof_result.status.value
        if proof_result.status == LeanProofStatus.RUNNING:
            status_text = f"{Spinner('dots')} [yellow]{status}[/yellow]"
        elif proof_result.status == LeanProofStatus.FINISHED:
            # Check if the result indicates a proof was found
            if proof_result.result and proof_result.result.get("sorries", 0) == 0 and proof_result.result.get("proof", ""):
                 status_text = f"[green]PROVED[/green] 🎉"
            else:
                 status_text = f"[red]FAILED[/red] ❌"
        elif proof_result.status == LeanProofStatus.ERROR:
            status_text = f"[red]ERROR[/red] ❌"
        else: # PENDING
            status_text = status

        # We need the original proof id, which is not in ProofResult, so let's fake it for display
        # This is a limitation of the current client API design
        table.add_row(filename, "N/A", status_text)
    return table


async def main():
    """Submit multiple proofs and display their status in a live table."""
    demo_dir = Path(__file__).parent
    lean_files = [
        demo_dir / "test.lean",
        demo_dir / "test2.lean",
        demo_dir / "test3.lean",
        demo_dir / "test4.lean",
    ]

    async with AsyncLeanClient(base_url="http://0.0.0.0:8080", timeout=60.0) as client:
        # Submit all proofs concurrently
        submitted_proofs: List[Proof] = await asyncio.gather(
            *[client.submit(proof=file) for file in lean_files]
        )

        # Map filename to submitted proof object
        proof_map: Dict[str, Proof] = {
            file.name: proof for file, proof in zip(lean_files, submitted_proofs)
        }
        
        # Store the status results
        results_status: Dict[str, ProofResult] = {}

        with Live(generate_table(results_status), refresh_per_second=4, transient=True) as live:
            pending_proofs = list(proof_map.items())

            while pending_proofs:
                # Query status for all pending proofs
                tasks = [client.get_result(proof=p) for _, p in pending_proofs]
                query_results: List[ProofResult] = await asyncio.gather(*tasks)

                newly_pending = []
                for (filename, proof), result in zip(pending_proofs, query_results):
                    results_status[filename] = result
                    # If the proof is not finished, add it to the list for the next query round
                    if result.status not in {LeanProofStatus.FINISHED, LeanProofStatus.ERROR}:
                        newly_pending.append((filename, proof))
                
                pending_proofs = newly_pending
                
                # Update the live table display
                # Re-generate the table with UUIDs from the original proofs
                display_table = Table(title="Lean Proof Status")
                display_table.add_column("File", justify="left", style="cyan", no_wrap=True)
                display_table.add_column("UUID", justify="left", style="magenta")
                display_table.add_column("Status", justify="left")

                for fname, p_obj in proof_map.items():
                    res = results_status.get(fname)
                    status_text = "PENDING"
                    if res:
                        status = res.status.value
                        if res.status == LeanProofStatus.RUNNING:
                            status_text = f"{Spinner('dots')} [yellow]{status}[/yellow]"
                        elif res.status == LeanProofStatus.FINISHED:
                            if res.result and res.result.get("sorries", 0) == 0 and res.result.get("tactic_proof"):
                                status_text = f"[green]PROVED[/green] 🎉"
                            else:
                                status_text = f"[red]FAILED[/red] ❌"
                        elif res.status == LeanProofStatus.ERROR:
                            status_text = f"[red]ERROR[/red] ❌"
                        else:
                            status_text = status
                    
                    display_table.add_row(fname, str(p_obj.id), status_text)

                live.update(display_table)
                if not pending_proofs:
                    break
                await asyncio.sleep(1)
        
        # Final table print
        console.print(generate_table(results_status))


if __name__ == "__main__":
    console = Console()
    try:
        asyncio.run(main())
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
