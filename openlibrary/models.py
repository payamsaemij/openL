"""Data models for Open Library."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Book:
    """Represents a book returned by Open Library."""

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
        """Return the canonical Open Library URL."""
        return f"https://openlibrary.org{self.key}"

    @classmethod
    def from_api(cls, data: dict) -> "Book":
        """Convert an API document into a Book instance."""
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