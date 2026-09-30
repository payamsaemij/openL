"""HTTP client for the Open Library API."""

import requests


class OpenLibraryClient:
    """A small client for Open Library search."""

    BASE_URL = "https://openlibrary.org/search.json"

    FIELDS = [
        "key",
        "title",
        "author_name",
        "first_publish_year",
        "edition_count",
        "isbn",
        "subject",
        "language",
    ]

    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OpenLibraryCLI/1.0 (research application)"
        })

    def search(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """Search books and return the API response."""
        params = {
            "q": query,
            "fields": ",".join(self.FIELDS),
            "limit": limit,
            "offset": offset,
        }

        response = self.session.get(
            self.BASE_URL,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self.session.close()

    def __enter__(self) -> "OpenLibraryClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()