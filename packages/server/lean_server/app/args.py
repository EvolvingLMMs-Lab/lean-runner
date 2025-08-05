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
        default=4,
        help="Maximum number of concurrent Lean worker threads.",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Reload the server when code changes are detected.",
    )
    return parser.parse_args()
