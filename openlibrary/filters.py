"""Book filtering utilities."""

from openlibrary.models import Book


def matches_pattern(book: Book, pattern: str) -> bool:
    """Check whether the pattern occurs in the book title."""
    return pattern.casefold() in book.title.casefold()


def is_published_after(book: Book, year: int) -> bool:
    """Check whether the first publication year is after year."""
    return book.first_publish_year > year


def is_valid_book(
    book: Book,
    pattern: str,
    after_year: int,
) -> bool:
    """Apply all book selection criteria."""
    return (
        bool(book.key)
        and bool(book.title.strip())
        and matches_pattern(book, pattern)
        and is_published_after(book, after_year)
    )