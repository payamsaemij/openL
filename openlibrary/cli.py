"""Command-line interface."""

import argparse
import logging

from openlibrary.client import OpenLibraryClient
from openlibrary.exporter import export_to_csv
from openlibrary.service import BookService


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser.

    Returns:
        argparse.ArgumentParser: Parser with all CLI options configured.
    """
    parser = argparse.ArgumentParser(
        prog="openlibrary",
        description=(
            "Fetch books from Open Library and export them to CSV."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-n", "--count",
        type=int,
        default=50,
        help="Number of books to collect.",
    )
    parser.add_argument(
        "-o", "--output",
        default="books.csv",
        help="Destination CSV file.",
    )
    parser.add_argument(
        "-p", "--pattern",
        default="lore",
        help="Pattern to match in book titles.",
    )
    parser.add_argument(
        "-y", "--after-year",
        type=int,
        default=2000,
        help="Only include books first published after this year.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging.",
    )

    return parser


def configure_logging(verbose: bool) -> None:
    """Configure root logging for the CLI run.

    Args:
        verbose (bool): If True, log at INFO level; else WARNING only.
    """
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )


def run(args: argparse.Namespace) -> int:
    """Execute the pipeline: validate, fetch, filter, and export books.

    Args:
        args (argparse.Namespace): Parsed CLI arguments.

    Raises:
        ValueError: If book count is not greater than zero.
        ValueError: If the search pattern is empty.

    Returns:
        int: Exit code; 0 on success, 1 when no books matched.
    """
    configure_logging(args.verbose)

    if args.count <= 0:
        raise ValueError("Book count must be greater than zero.")

    if not args.pattern.strip():
        raise ValueError("Search pattern cannot be empty.")

    print("\n Open Library Book Collector")
    print(" " + "─" * 32)
    print(f" Pattern    : {args.pattern}")
    print(f" After year : {args.after_year}")
    print(f" Book count : {args.count}")
    print(f" Output     : {args.output}")
    print(" " + "─" * 32 + "\n")

    with OpenLibraryClient() as client:
        service = BookService(client)
        books = service.fetch_books(
            count=args.count,
            pattern=args.pattern,
            after_year=args.after_year,
        )

    if not books:
        print("No matching books found. No CSV file was created.")
        return 1

    output_path = export_to_csv(books, args.output)

    print("\n Collection completed!")
    print(f" Books collected : {len(books)}")
    print(f" CSV file        : {output_path.resolve()}")
    print("\n Done.\n")

    return 0


def main() -> int:
    """CLI entry point: parse arguments and handle common errors.

    Returns:
        int: Process exit code.
    """
    parser = build_parser()
    args = parser.parse_args()

    try:
        return run(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 130
    except (ValueError, OSError) as error:
        parser.error(str(error))
    except Exception as error:
        logging.exception("Unexpected error: %s", error)
        return 1

    return 0