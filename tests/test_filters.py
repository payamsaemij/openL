
import unittest

from openlibrary.filters import (
    matches_pattern,
    is_published_after,
    is_valid_book,
)
from tests.helpers import make_book


class TestMatchesPattern(unittest.TestCase):
    def test_matches_pattern_in_title(self):
        book = make_book(title="The Lore of the Forest")

        self.assertTrue(matches_pattern(book, "lore"))

    def test_pattern_is_case_insensitive(self):
        book = make_book(title="THE LORE")

        self.assertTrue(matches_pattern(book, "lOrE"))

    def test_returns_false_when_pattern_missing(self):
        book = make_book(title="The Forest")

        self.assertFalse(matches_pattern(book, "lore"))

    def test_empty_pattern_matches_any_title(self):
        book = make_book(title="The Forest")

        self.assertTrue(matches_pattern(book, ""))


class TestIsPublishedAfter(unittest.TestCase):
    def test_year_after_threshold(self):
        book = make_book(first_publish_year=2010)

        self.assertTrue(is_published_after(book, 2000))

    def test_year_equal_to_threshold_is_not_after(self):
        book = make_book(first_publish_year=2000)

        self.assertFalse(is_published_after(book, 2000))

    def test_year_before_threshold(self):
        book = make_book(first_publish_year=1995)

        self.assertFalse(is_published_after(book, 2000))

    def test_missing_year_returns_false(self):
        book = make_book(first_publish_year=None)

        self.assertFalse(is_published_after(book, 2000))


class TestIsValidBook(unittest.TestCase):
    def test_valid_book(self):
        book = make_book(
            key="/works/OL123W",
            title="The Lore",
            first_publish_year=2010,
        )

        self.assertTrue(is_valid_book(book, "lore", 2000))

    def test_rejects_missing_key(self):
        book = make_book(key="")

        self.assertFalse(is_valid_book(book, "lore", 2000))

    def test_rejects_missing_title(self):
        book = make_book(title="")

        self.assertFalse(is_valid_book(book, "lore", 2000))

    def test_rejects_non_matching_pattern(self):
        book = make_book(title="The Forest")

        self.assertFalse(is_valid_book(book, "lore", 2000))

    def test_rejects_old_publication_year(self):
        book = make_book(first_publish_year=1990)

        self.assertFalse(is_valid_book(book, "lore", 2000))


if __name__ == "__main__":
    unittest.main()
