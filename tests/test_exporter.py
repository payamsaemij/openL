
import csv
import tempfile
import unittest
from pathlib import Path

from openlibrary.exporter import (
    CSV_FIELDS,
    book_to_row,
    export_to_csv,
)
from tests.helpers import make_book


class TestBookToRow(unittest.TestCase):
    def test_converts_book_to_csv_row(self):
        book = make_book(
            key="/works/OL123W",
            title="The Lore",
            authors=("Jane Author", "John Writer"),
            first_publish_year=2010,
            edition_count=4,
            isbns=("123", "456"),
            subjects=("Fantasy", "Adventure"),
            languages=("eng", "fre"),
        )

        row = book_to_row(book)

        self.assertEqual(row["key"], "/works/OL123W")
        self.assertEqual(row["title"], "The Lore")
        self.assertIn("Jane Author", row["authors"])
        self.assertIn("John Writer", row["authors"])
        self.assertEqual(row["first_publish_year"], 2010)
        self.assertEqual(row["edition_count"], 4)
        self.assertIn("123", row["isbns"])
        self.assertIn("Fantasy", row["subjects"])
        self.assertIn("eng", row["languages"])
        self.assertEqual(row["url"], book.url)


class TestExportToCsv(unittest.TestCase):
    def test_creates_csv_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "books.csv"
            books = [
                make_book(key="/works/OL1W", title="The Lore"),
                make_book(key="/works/OL2W", title="Lore Again"),
            ]

            result = export_to_csv(books, output)

            self.assertTrue(output.exists())
            self.assertEqual(Path(result), output)

    def test_csv_contains_header_and_rows(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "books.csv"
            books = [
                make_book(
                    key="/works/OL1W",
                    title="The Lore",
                ),
                make_book(
                    key="/works/OL2W",
                    title="Lore Again",
                ),
            ]

            export_to_csv(books, output)

            with output.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)

            self.assertEqual(reader.fieldnames, CSV_FIELDS)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["title"], "The Lore")
            self.assertEqual(rows[1]["title"], "Lore Again")

    def test_creates_missing_parent_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = (
                Path(temp_dir)
                / "nested"
                / "folder"
                / "books.csv"
            )

            export_to_csv(
                [make_book()],
                output,
            )

            self.assertTrue(output.exists())
            self.assertTrue(output.parent.is_dir())

    def test_exports_empty_book_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "empty.csv"

            export_to_csv([], output)

            self.assertTrue(output.exists())

            with output.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                self.assertEqual(list(reader), [])

    def test_csv_uses_expected_columns(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "books.csv"

            export_to_csv([make_book()], output)

            with output.open(
                "r",
                encoding="utf-8-sig",
                newline="",
            ) as csv_file:
                reader = csv.DictReader(csv_file)
                self.assertEqual(reader.fieldnames, CSV_FIELDS)


if __name__ == "__main__":
    unittest.main()