"""Book filtering utilities."""

from openlibrary.models import Book


def matches_pattern(book: Book, pattern: str) -> bool:
    """Check if the pattern appears in the title, ignoring case.

    Args:
        book (Book): Book whose title is checked.
        pattern (str): Substring to search for.

    Returns:
        bool: True if the title contains the pattern.
    """
    return pattern.casefold() in book.title.casefold()


def is_published_after(book: Book, year: int) -> bool:
    """Check if the book was first published after the given year.

    Books with an unknown publish year never match.

    Args:
        book (Book): Book whose publish year is checked.
        year (int): Cutoff year (exclusive).

    Returns:
        bool: True if first_publish_year is set and greater than year.
    """
    return (
        book.first_publish_year is not None
        and book.first_publish_year > year
    )


def is_valid_book(
    book: Book,
    pattern: str,
    after_year: int,
) -> bool:
    """Check whether a book passes every collection filter.

    A book is valid when it has a key and a non-blank title, matches
    the pattern, and was first published after the cutoff year.

    Args:
        book (Book): Book to validate.
        pattern (str): Substring required in the title.
        after_year (int): Cutoff year (exclusive).

    Returns:
        bool: True if all checks pass.
    """
    return (
        bool(book.key)
        and bool(book.title.strip())
        and matches_pattern(book, pattern)
        and is_published_after(book, after_year)
    )