
import unittest
from unittest.mock import Mock, patch

from openlibrary.service import BookService
from tests.helpers import make_api_book


class TestBookService(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.service = BookService(
            client=self.client,
            page_size=2,
            delay=0,
        )

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_returns_matching_books(self, mock_sleep):
        self.client.search.return_value = {
            "numFound": 2,
            "docs": [
                make_api_book(
                    key="/works/OL1W",
                    title="The Lore",
                    first_publish_year=2010,
                ),
                make_api_book(
                    key="/works/OL2W",
                    title="Lore of Magic",
                    first_publish_year=2015,
                ),
            ],
        }

        books = self.service.fetch_books(
            count=2,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 2)
        self.assertEqual(
            [book.key for book in books],
            ["/works/OL1W", "/works/OL2W"],
        )

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_respects_requested_count(self, mock_sleep):
        self.client.search.return_value = {
            "numFound": 3,
            "docs": [
                make_api_book(key="/works/OL1W"),
                make_api_book(key="/works/OL2W"),
                make_api_book(key="/works/OL3W"),
            ],
        }

        books = self.service.fetch_books(
            count=1,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 1)

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_filters_old_books(self, mock_sleep):
        self.client.search.return_value = {
            "numFound": 2,
            "docs": [
                make_api_book(
                    key="/works/OL1W",
                    first_publish_year=1990,
                ),
                make_api_book(
                    key="/works/OL2W",
                    first_publish_year=2010,
                ),
            ],
        }

        books = self.service.fetch_books(
            count=10,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].key, "/works/OL2W")

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_filters_non_matching_titles(
        self,
        mock_sleep,
    ):
        self.client.search.return_value = {
            "numFound": 2,
            "docs": [
                make_api_book(
                    key="/works/OL1W",
                    title="The Lore",
                ),
                make_api_book(
                    key="/works/OL2W",
                    title="A Forest Story",
                ),
            ],
        }

        books = self.service.fetch_books(
            count=10,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].key, "/works/OL1W")

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_deduplicates_by_key(self, mock_sleep):
        self.client.search.return_value = {
            "numFound": 3,
            "docs": [
                make_api_book(key="/works/OL1W"),
                make_api_book(key="/works/OL1W"),
                make_api_book(key="/works/OL2W"),
            ],
        }

        books = self.service.fetch_books(
            count=10,
            pattern="lore",
            after_year=2000,
        )

        keys = [book.key for book in books]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(books), 2)

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_requests_multiple_pages(self, mock_sleep):
        self.client.search.side_effect = [
            {
                "numFound": 4,
                "docs": [
                    make_api_book(key="/works/OL1W"),
                    make_api_book(key="/works/OL2W"),
                ],
            },
            {
                "numFound": 4,
                "docs": [
                    make_api_book(key="/works/OL3W"),
                    make_api_book(key="/works/OL4W"),
                ],
            },
        ]

        books = self.service.fetch_books(
            count=4,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 4)
        self.assertEqual(self.client.search.call_count, 2)

        first_call = self.client.search.call_args_list[0]
        second_call = self.client.search.call_args_list[1]

        self.assertEqual(first_call.kwargs["offset"], 0)
        self.assertEqual(second_call.kwargs["offset"], 2)

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_stops_when_no_more_results(
        self,
        mock_sleep,
    ):
        self.client.search.return_value = {
            "numFound": 0,
            "docs": [],
        }

        books = self.service.fetch_books(
            count=10,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(books, [])
        self.assertEqual(self.client.search.call_count, 1)

    @patch("openlibrary.service.time.sleep")
    def test_fetch_books_skips_malformed_documents(
        self,
        mock_sleep,
    ):
        self.client.search.return_value = {
            "numFound": 2,
            "docs": [
                None,
                make_api_book(key="/works/OL2W"),
            ],
        }

        books = self.service.fetch_books(
            count=10,
            pattern="lore",
            after_year=2000,
        )

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].key, "/works/OL2W")

    def test_fetch_books_rejects_non_positive_count(self):
        with self.assertRaises(ValueError):
            self.service.fetch_books(
                count=0,
                pattern="lore",
                after_year=2000,
            )


if __name__ == "__main__":
    unittest.main()
