"""HTTP client for the Open Library API."""

import requests


class OpenLibraryClient:
    """HTTP client for the Open Library search API.

    Keeps one requests session alive across calls and supports use as
    a context manager.
    """

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
        """Create a client with a shared HTTP session.

        Args:
            timeout (int, optional): Per-request timeout in seconds.
                Defaults to 30.
        """
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
        """Search books and return the parsed JSON response.

        Args:
            query (str): Free-text search query.
            limit (int, optional): Results per page. Defaults to 100.
            offset (int, optional): Pagination offset. Defaults to 0.

        Returns:
            dict: Decoded JSON with "docs" and "numFound" keys.

        Raises:
            requests.HTTPError: If the API returns an error status.
        """
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
        """Return the client itself for use in a with block."""
        return self

    def __exit__(self, *args: object) -> None:
        """Close the session when exiting the with block."""
        self.close()
