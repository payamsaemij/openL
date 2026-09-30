# Open Library CLI

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)

A command-line tool that searches the [Open Library](https://openlibrary.org) API for books matching a title pattern and publication window, then exports the results to a clean, analysis-ready CSV file.

Built with a small, layered architecture (client → service → filters → exporter) and covered by a full unit-test suite.

## Features

- **Keyword search** — queries the Open Library Search API and matches a case-insensitive pattern against book titles.
- **Publication filter** — keeps only books first published after a configurable year.
- **Automatic pagination** — fetches results page by page until the requested number of books is collected or the result set is exhausted.
- **Deduplication & validation** — skips malformed records and duplicate works using Open Library work keys.
- **Polite API usage** — requests only the fields it needs, reuses one HTTP session, and throttles between pages.
- **CSV export** — writes a UTF-8 (BOM) CSV that opens correctly in Excel, Pandas, and most other tools.
- **Helpful CLI** — sensible defaults, clear progress logging, and meaningful exit codes.

## How It Works

```
Open Library API
      │
      ▼
OpenLibraryClient   HTTP access, field selection, timeouts
      │
      ▼
BookService         pagination, deduplication, retry-safe loop
      │
      ▼
filters             title-pattern and publication-year criteria
      │
      ▼
Book (model)        immutable dataclass built from API documents
      │
      ▼
exporter            CSV writer (utf-8-sig, auto-created directories)
```

## Project Structure

```
openL/
├── main.py                    # Entry point
├── openlibrary/
│   ├── __init__.py            # Package metadata (version)
│   ├── cli.py                 # Argument parsing and application flow
│   ├── client.py              # Open Library API HTTP client
│   ├── service.py             # Book collection orchestration
│   ├── filters.py             # Selection criteria
│   ├── models.py              # Book dataclass
│   └── exporter.py            # CSV export
└── tests/
    ├── helpers.py             # Shared test factories
    ├── test_client.py
    ├── test_cli.py
    ├── test_exporter.py
    ├── test_filters.py
    ├── test_models.py
    └── test_service.py
```

## Requirements

- Python **3.10+**
- [requests](https://pypi.org/project/requests/)

## Installation

```bash
# Clone the repository
git clone https://github.com/payamsaemij/openL.git
cd openL

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install requirements.txt
```

## Usage

```bash
python main.py [OPTIONS]
```

### Options

| Option | Short | Default | Description |
| --- | --- | --- | --- |
| `--count` | `-n` | `50` | Number of books to collect. |
| `--output` | `-o` | `books.csv` | Destination CSV file. |
| `--pattern` | `-p` | `lore` | Pattern to match in book titles (case-insensitive). |
| `--after-year` | `-y` | `2000` | Only include books first published after this year. |
| `--verbose` | | off | Enable detailed INFO-level logging. |

### Examples

Collect the default 50 books with the default settings:

```bash
python main.py
```

Collect 100 books with "Lore" in the title, published after 2010:

```bash
python main.py --pattern Lore --after-year 2010 --count 100
```

Save to a custom location with verbose progress logging:

```bash
python main.py -p history -y 1990 -n 25 -o exports/history_books.csv --verbose
```

### Example Output

```
 Open Library Book Collector
 ────────────────────────────────
 Pattern    : lore
 After year : 2000
 Book count : 50
 Output     : books.csv
 ────────────────────────────────

 Collection completed!
 Books collected : 50
 CSV file        : /home/user/openL/books.csv

 Done.
```

## CSV Output

The exported file contains one row per book with the following columns:

| Column | Description |
| --- | --- |
| `key` | Unique Open Library work key. |
| `title` | Book title. |
| `authors` | Author names, joined with `; `. |
| `first_publish_year` | Year of first publication. |
| `edition_count` | Number of known editions. |
| `isbns` | Up to 5 ISBNs, joined with `; `. |
| `subjects` | Up to 10 subjects, joined with `; `. |
| `languages` | Language codes (e.g. `eng`), joined with `; `. |
| `url` | Canonical Open Library page URL. |

## Development

### Running Tests

The test suite uses `unittest` and runs with either pytest or the standard library:

```bash
# With pytest
pip install pytest
python -m pytest

# Or with the standard library
python -m unittest discover -s tests
```

All tests run against mocks — no network access is required.

### Code Layout Notes

- **`models.Book`** is a frozen, slotted dataclass; `Book.from_api()` converts a raw API document, defensively handling missing fields.
- **`client.OpenLibraryClient`** is a context manager that reuses a `requests.Session` with a custom `User-Agent` and request timeout.
- **`service.BookService`** owns the collection loop: pagination, deduplication by work key, validation, and throttling (`delay` between page requests).
- **`filters`** isolate the selection criteria (`matches_pattern`, `is_published_after`, `is_valid_book`) so they can be tested independently.
- **`exporter.export_to_csv`** creates parent directories as needed and writes UTF-8 with BOM for Excel compatibility.

## Exit Codes

| Code | Meaning |
| --- | --- |
| `0` | Success — CSV file written. |
| `1` | No matching books found, or an unexpected error occurred. |
| `130` | Cancelled by the user (`Ctrl+C`). |

## Acknowledgments

Book data is provided by [Open Library](https://openlibrary.org), a project of the [Internet Archive](https://archive.org). Please respect their [API usage guidelines](https://openlibrary.org/developers/api) when running large collections.
