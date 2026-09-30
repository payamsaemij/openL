
import unittest

from openlibrary.models import Book
from tests.helpers import make_api_book


class TestBook(unittest.TestCase):
    def test_book_url(self):
        book = Book(
            key="/works/OL123W",
            title="The Lore",
            authors=("Jane Author",),
            first_publish_year=2010,
            edition_count=2,
            isbns=(),
            subjects=(),
            languages=(),
        )

        self.assertEqual(
            book.url,
            "https://openlibrary.org/works/OL123W",
        )

    def test_from_api_maps_fields(self):
        data = make_api_book()
        book = Book.from_api(data)

        self.assertEqual(book.key, "/works/OL123W")
        self.assertEqual(book.title, "The Lore of the Forest")
        self.assertEqual(book.authors, ("Jane Author",))
        self.assertEqual(book.first_publish_year, 2010)
        self.assertEqual(book.edition_count, 3)
        self.assertEqual(book.isbns, ("9781234567890",))
        self.assertEqual(book.subjects, ("Fantasy", "Forest"))
        self.assertEqual(book.languages, ("eng",))

    def test_from_api_handles_missing_optional_fields(self):
        book = Book.from_api({
            "key": "/works/OL456W",
            "title": "Untitled Book",
        })

        self.assertEqual(book.key, "/works/OL456W")
        self.assertEqual(book.title, "Untitled Book")
        self.assertEqual(book.authors, ())
        self.assertIsNone(book.first_publish_year)
        self.assertEqual(book.edition_count, 0)
        self.assertEqual(book.isbns, ())
        self.assertEqual(book.subjects, ())
        self.assertEqual(book.languages, ())

    def test_from_api_limits_isbns_and_subjects(self):
        data = {
            "key": "/works/OL789W",
            "title": "Long Lists",
            "isbn": [f"isbn-{i}" for i in range(10)],
            "subject": [f"subject-{i}" for i in range(15)],
        }

        book = Book.from_api(data)

        self.assertEqual(len(book.isbns), 5)
        self.assertEqual(len(book.subjects), 10)

    def test_from_api_handles_empty_title(self):
        book = Book.from_api({
            "key": "/works/OL111W",
        })

        self.assertEqual(book.title, "")


if __name__ == "__main__":
    unittest.main()
