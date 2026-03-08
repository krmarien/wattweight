"""Main module for wattweight."""

import argparse
import sys


def main() -> int:
    """Main entry point for the wattweight application."""
    parser = argparse.ArgumentParser(
        description="Wattweight - Energy management tool",
        prog="wattweight"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands"
    )
    
    # Add example subcommand
    analyze_parser = subparsers.add_parser("analyze", help="Analyze energy data")
    analyze_parser.add_argument("file", help="Data file to analyze")
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Verbose mode enabled")
    
    if args.command == "analyze":
        print(f"Analyzing file: {args.file}")
        return 0
    elif args.command is None:
        parser.print_help()
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
