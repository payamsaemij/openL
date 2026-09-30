"""Application service for collecting books."""

import logging
import time

from openlibrary.client import OpenLibraryClient
from openlibrary.filters import is_valid_book
from openlibrary.models import Book

logger = logging.getLogger(__name__)


class BookService:
    """Collect filtered books from Open Library, page by page.

    Attributes:
        client (OpenLibraryClient): Client used for search requests.
        page_size (int): Results requested per API call.
        delay (float): Pause in seconds between consecutive pages.
    """

    def __init__(
        self,
        client: OpenLibraryClient,
        page_size: int = 100,
        delay: float = 0.2,
    ) -> None:
        """Store the API client and pagination settings.

        Args:
            client (OpenLibraryClient): Client used to query the API.
            page_size (int, optional): Results per request.
                Defaults to 100.
            delay (float, optional): Pause between requests in seconds.
                Defaults to 0.2.
        """
        self.client = client
        self.page_size = page_size
        self.delay = delay

    def fetch_books(
        self,
        count: int,
        pattern: str,
        after_year: int,
    ) -> list[Book]:
        """Collect up to count books matching pattern and after_year.

        Pages through search results, skipping duplicates and invalid
        records, and stops early when results run out.

        Args:
            count (int): Maximum number of books to collect.
            pattern (str): Required title substring; also the API query.
            after_year (int): Keep only books first published after
                this year.

        Raises:
            ValueError: If count is not greater than zero.
            ValueError: If pattern is empty or only whitespace.
            ValueError: If page_size is not greater than zero.

        Returns:
            list[Book]: Matching books, at most count entries.
        """
        if count <= 0:
            raise ValueError(
                "Book count must be greater than zero."
            )

        if not pattern or not pattern.strip():
            raise ValueError(
                "Search pattern cannot be empty."
            )

        if self.page_size <= 0:
            raise ValueError(
                "Page size must be greater than zero."
            )

        books: list[Book] = []
        seen: set[str] = set()
        offset = 0

        while len(books) < count:
            logger.info(
                "Fetching API page at offset %d", offset
            )

            data = self.client.search(
                query=pattern,
                limit=self.page_size,
                offset=offset,
            )

            documents = data.get("docs", [])
            total = data.get("numFound", 0)

            if not documents:
                logger.info("No more search results.")
                break

            for document in documents:
                if not isinstance(document, dict):
                    logger.warning(
                        "Skipping invalid book document: %r",
                        document,
                    )
                    continue

                key = document.get("key")

                if not key or key in seen:
                    continue

                try:
                    book = Book.from_api(document)
                except (KeyError, TypeError, ValueError):
                    logger.warning(
                        "Skipping invalid book record: %s",
                        key,
                    )
                    continue

                if not is_valid_book(
                    book, pattern, after_year
                ):
                    continue

                books.append(book)
                seen.add(key)

                logger.info(
                    "Matched %d/%d: %s (%s)",
                    len(books),
                    count,
                    book.title,
                    book.first_publish_year,
                )

                if len(books) >= count:
                    break

            offset += len(documents)

            if offset >= total:
                logger.info(
                    "Reached end of search results."
                )
                break

            if self.delay > 0:
                time.sleep(self.delay)

        return books