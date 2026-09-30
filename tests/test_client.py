
import unittest
from unittest.mock import Mock, patch

import requests

from openlibrary.client import OpenLibraryClient


class TestOpenLibraryClient(unittest.TestCase):
    def setUp(self):
        self.client = OpenLibraryClient()
        self.addCleanup(self.client.close)

    @patch("openlibrary.client.requests.Session.get")
    def test_search_sends_expected_request(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "docs": [],
            "numFound": 0,
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = self.client.search(
            query="lore",
            limit=50,
            offset=10,
        )

        self.assertEqual(result["docs"], [])
        mock_get.assert_called_once()

        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], self.client.BASE_URL)
        self.assertEqual(
            kwargs["params"]["q"],
            "lore",
        )
        self.assertEqual(
            kwargs["params"]["limit"],
            50,
        )
        self.assertEqual(
            kwargs["params"]["offset"],
            10,
        )
        self.assertIn("timeout", kwargs)

    @patch("openlibrary.client.requests.Session.get")
    def test_search_returns_json_response(self, mock_get):
        expected = {
            "docs": [{"key": "/works/OL1W"}],
            "numFound": 1,
        }

        response = Mock()
        response.json.return_value = expected
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        result = self.client.search("lore")

        self.assertEqual(result, expected)

    @patch("openlibrary.client.requests.Session.get")
    def test_search_raises_http_error(self, mock_get):
        response = Mock()
        response.raise_for_status.side_effect = (
            requests.HTTPError("HTTP error")
        )
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            self.client.search("lore")

    @patch("openlibrary.client.requests.Session.get")
    def test_search_raises_connection_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError(
            "Connection failed"
        )

        with self.assertRaises(requests.ConnectionError):
            self.client.search("lore")

    @patch("openlibrary.client.requests.Session.get")
    def test_search_raises_invalid_json_error(self, mock_get):
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = response

        with self.assertRaises(ValueError):
            self.client.search("lore")

    def test_client_supports_context_manager(self):
        with OpenLibraryClient() as client:
            self.assertIsNotNone(client)

    def test_close_closes_session(self):
        client = OpenLibraryClient()
        with patch.object(client.session, "close") as mock_close:
            client.close()

        mock_close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
