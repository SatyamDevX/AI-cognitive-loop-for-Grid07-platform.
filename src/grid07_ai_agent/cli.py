"""Command-line demos for assignment phases."""

from __future__ import annotations

import argparse
import json

from grid07_ai_agent.router import route_post_to_bots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Grid07 AI agent demos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    route_parser = subparsers.add_parser("route", help="Route a post to matching bots")
    route_parser.add_argument("post_content", help="Incoming post content")
    route_parser.add_argument("--threshold", type=float, default=0.85)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "route":
        payload = {
            "post_content": args.post_content,
            "matched_bots": route_post_to_bots(args.post_content, threshold=args.threshold),
        }
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

