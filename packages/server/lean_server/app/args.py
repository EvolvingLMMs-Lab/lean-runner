import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Lean Server.")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="The host to bind the server to."
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="The port to run the server on."
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=32,
        help="Maximum number of concurrent Lean worker threads.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="default",
        help="Path to a custom configuration file.",
    )
    parser.add_argument(
        "--lean-workspace",
        type=str,
        default="default",
        help="Path to the Lean workspace.",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level for the server.",
    )
    return parser.parse_args()
