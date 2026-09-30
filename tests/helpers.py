
from openlibrary.models import Book


def make_book(
    key="/works/OL123W",
    title="The Lore of the Forest",
    authors=("Jane Author",),
    first_publish_year=2010,
    edition_count=3,
    isbns=("9781234567890",),
    subjects=("Fantasy", "Forest"),
    languages=("eng",),
):
    return Book(
        key=key,
        title=title,
        authors=authors,
        first_publish_year=first_publish_year,
        edition_count=edition_count,
        isbns=isbns,
        subjects=subjects,
        languages=languages,
    )


def make_api_book(
    key="/works/OL123W",
    title="The Lore of the Forest",
    author_name=None,
    first_publish_year=2010,
    edition_count=3,
    isbn=None,
    subject=None,
    language=None,
):
    return {
        "key": key,
        "title": title,
        "author_name": author_name or ["Jane Author"],
        "first_publish_year": first_publish_year,
        "edition_count": edition_count,
        "isbn": isbn or ["9781234567890"],
        "subject": subject or ["Fantasy", "Forest"],
        "language": language or ["eng"],
    }
