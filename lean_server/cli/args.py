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
        "--config", type=str, default="AUTO", help="The config to use for the server."
    )
    return parser.parse_args()
