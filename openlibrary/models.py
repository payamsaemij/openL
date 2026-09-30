"""Data models for Open Library."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Book:
    """Immutable record for a single Open Library book.

    Attributes:
        key (str): Open Library work key, e.g. "/works/OL123W".
        title (str): Book title; may be empty in raw API data.
        authors (tuple[str, ...]): Author names.
        first_publish_year (int | None): First publication year, if known.
        edition_count (int): Number of known editions.
        isbns (tuple[str, ...]): Up to five ISBN values.
        subjects (tuple[str, ...]): Up to ten subject headings.
        languages (tuple[str, ...]): Language codes of the editions.
    """

    key: str
    title: str
    authors: tuple[str, ...]
    first_publish_year: int | None
    edition_count: int
    isbns: tuple[str, ...]
    subjects: tuple[str, ...]
    languages: tuple[str, ...]

    @property
    def url(self) -> str:
        """Build the public Open Library URL for this book.

        Returns:
            str: Full URL, e.g. "https://openlibrary.org/works/OL123W".
        """
        return f"https://openlibrary.org{self.key}"

    @classmethod
    def from_api(cls, data: dict) -> "Book":
        """Build a Book from one raw search-API document.

        Missing optional fields fall back to empty values; isbns are
        capped at 5 entries and subjects at 10.

        Args:
            data (dict): Single entry from the API's "docs" list.

        Returns:
            Book: Parsed book instance.

        Raises:
            KeyError: If the document has no "key" field.
        """
        return cls(
            key=data["key"],
            title=data.get("title", ""),
            authors=tuple(data.get("author_name") or ()),
            first_publish_year=data.get("first_publish_year"),
            edition_count=data.get("edition_count", 0),
            isbns=tuple((data.get("isbn") or [])[:5]),
            subjects=tuple((data.get("subject") or [])[:10]),
            languages=tuple(data.get("language") or []),
        )
