
import argparse
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from openlibrary import cli
from tests.helpers import make_book


class TestBuildParser(unittest.TestCase):

    def test_parser_defaults(self):
        args = cli.build_parser().parse_args([])

        self.assertEqual(args.count, 50)
        self.assertEqual(args.output, "books.csv")
        self.assertEqual(args.pattern, "lore")
        self.assertEqual(args.after_year, 2000)
        self.assertFalse(args.verbose)

    def test_parser_custom_arguments(self):
        args = cli.build_parser().parse_args([
            "--count", "25",
            "--output", "results.csv",
            "--pattern", "dragon",
            "--after-year", "2010",
            "--verbose",
        ])

        self.assertEqual(args.count, 25)
        self.assertEqual(args.output, "results.csv")
        self.assertEqual(args.pattern, "dragon")
        self.assertEqual(args.after_year, 2010)
        self.assertTrue(args.verbose)


class TestRun(unittest.TestCase):

    def make_args(self, **overrides):
        values = {
            "count": 2,
            "output": "books.csv",
            "pattern": "lore",
            "after_year": 2000,
            "verbose": False,
        }
        values.update(overrides)
        return argparse.Namespace(**values)

    @patch("openlibrary.cli.export_to_csv")
    @patch("openlibrary.cli.BookService")
    @patch("openlibrary.cli.OpenLibraryClient")
    def test_run_fetches_and_exports_books(
        self, mock_client, mock_service, mock_export
    ):
        books = [make_book()]
        mock_service.return_value.fetch_books.return_value = books
        mock_export.return_value = Path("books.csv")

        result = cli.run(self.make_args())

        self.assertEqual(result, 0)
        mock_client.assert_called_once_with()
        mock_service.assert_called_once_with(
            mock_client.return_value.__enter__.return_value
        )
        mock_service.return_value.fetch_books.assert_called_once_with(
            count=2,
            pattern="lore",
            after_year=2000,
        )
        mock_export.assert_called_once_with(
            books, "books.csv"
        )

    @patch("openlibrary.cli.export_to_csv")
    @patch("openlibrary.cli.BookService")
    @patch("openlibrary.cli.OpenLibraryClient")
    def test_run_handles_no_books(
        self, mock_client, mock_service, mock_export
    ):
        mock_service.return_value.fetch_books.return_value = []

        result = cli.run(self.make_args())

        self.assertEqual(result, 1)
        mock_export.assert_not_called()

    @patch("openlibrary.cli.OpenLibraryClient")
    def test_run_rejects_non_positive_count(self, mock_client):
        with self.assertRaises(ValueError):
            cli.run(self.make_args(count=0))

        mock_client.assert_not_called()

    @patch("openlibrary.cli.OpenLibraryClient")
    def test_run_rejects_empty_pattern(self, mock_client):
        with self.assertRaises(ValueError):
            cli.run(self.make_args(pattern=""))

        mock_client.assert_not_called()

    @patch("openlibrary.cli.export_to_csv")
    @patch("openlibrary.cli.BookService")
    @patch("openlibrary.cli.OpenLibraryClient")
    def test_run_handles_service_error(
        self, mock_client, mock_service, mock_export
    ):
        mock_service.return_value.fetch_books.side_effect = (
            RuntimeError("API unavailable")
        )

        with self.assertRaisesRegex(
            RuntimeError, "API unavailable"
        ):
            cli.run(self.make_args())

        mock_export.assert_not_called()


class TestMain(unittest.TestCase):

    @patch("openlibrary.cli.run", return_value=0)
    @patch("openlibrary.cli.build_parser")
    def test_main_parses_arguments_and_calls_run(
        self, mock_build_parser, mock_run
    ):
        mock_parser = MagicMock()
        mock_parser.parse_args.return_value = argparse.Namespace(
            count=10,
            output="books.csv",
            pattern="lore",
            after_year=2000,
            verbose=False,
        )
        mock_build_parser.return_value = mock_parser

        result = cli.main()

        self.assertEqual(result, 0)
        mock_parser.parse_args.assert_called_once_with()
        mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()