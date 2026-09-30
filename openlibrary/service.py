"""Application service for collecting books."""

import logging
import time

from openlibrary.client import OpenLibraryClient
from openlibrary.filters import is_valid_book
from openlibrary.models import Book

logger = logging.getLogger(__name__)


class BookService:
    """Collect matching books from Open Library."""

    def __init__(
        self,
        client: OpenLibraryClient,
        page_size: int = 100,
        delay: float = 0.2,
    ) -> None:
        self.client = client
        self.page_size = page_size
        self.delay = delay

    def fetch_books(
        self,
        count: int,
        pattern: str,
        after_year: int,
    ) -> list[Book]:
        """Fetch up to count unique matching books."""

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