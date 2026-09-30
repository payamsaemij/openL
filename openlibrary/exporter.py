"""CSV export utilities."""

import csv
from pathlib import Path

from openlibrary.models import Book


CSV_FIELDS = [
    "key",
    "title",
    "authors",
    "first_publish_year",
    "edition_count",
    "isbns",
    "subjects",
    "languages",
    "url",
]

def book_to_row(book: Book) -> dict[str, str | int | None]:
    """Convert a Book instance to a CSV row."""
    return {
        "key": book.key,
        "title": book.title,
        "authors": "; ".join(book.authors),
        "first_publish_year": book.first_publish_year,
        "edition_count": book.edition_count,
        "isbns": "; ".join(book.isbns),
        "subjects": "; ".join(book.subjects),
        "languages": "; ".join(book.languages),
        "url": book.url,
    }


def export_to_csv(
    books: list[Book],
    output: str | Path,
) -> Path:
    """Write books to a CSV file and return its path."""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=CSV_FIELDS,
        )
        writer.writeheader()
        writer.writerows(book_to_row(book) for book in books)

    return path