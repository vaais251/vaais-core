# VA-AIS Core File Structure

VA-AIS Core is a FastAPI service that extracts structured travel leads from
text. It supports a fixture-based mock provider and a live Gemini provider.

## Project layout

```text
vaais-core/
|-- app/                              # API application and extraction logic
|   |-- __init__.py                   # Python package marker
|   |-- main.py                       # /health and /extract endpoints
|   |-- schemas.py                    # Request, lead, and response models
|   |-- day2_pydantic.py               # Earlier schema prototype
|   |-- day3_fastapi_out_response.py   # Earlier API response prototype
|   `-- providers/                    # Interchangeable extraction providers
|       |-- __init__.py               # Provider package marker
|       |-- base.py                   # Provider interface and error classes
|       |-- factory.py                # Selects provider using environment settings
|       |-- fixture_loader.py         # Loads and validates mock fixture data
|       |-- mock.py                   # Returns labels for exact fixture matches
|       `-- gemini.py                 # Calls Gemini and validates its response
|-- data/                             # Development and test data
|   `-- fixtures.jsonl                # Ten travel inquiries with expected labels
|-- docs/                             # Requirements and development documentation
|   |-- api_contract.md               # Request format and example inquiries
|   |-- requirements.md               # Business rules and acceptance criteria
|   |-- DAY7_README.md                # Provider setup and verification notes
|   |-- day7_prospects.csv             # Tour-company prospect records
|   `-- file_structure.md             # This project layout guide
|-- src/
|   `-- vaais_core/                   # Installable package and console entry point
|       `-- __init__.py               # main() currently prints a greeting
|-- tests/                            # API, fixture, and provider tests
|   |-- __init__.py                   # Test package marker
|   |-- extraction_test.py            # Standalone health-check prototype
|   |-- test_health.py                # Legacy health-check test
|   |-- test_extract.py               # Endpoint and input validation tests
|   |-- test_fixture.py               # Fixture validation and legacy stub tests
|   |-- test_mock_provider.py         # Mock lookup and response isolation tests
|   `-- test_day7_providers.py         # Provider selection, errors, and SDK tests
|-- .env                              # Local provider settings and API key (ignored)
|-- .gitignore                        # Files and directories excluded from Git
|-- .python-version                   # Python version used by development tools
|-- pyproject.toml                    # Dependencies, build settings, and entry point
|-- uv.lock                           # Locked dependency versions
|-- README.md                         # Root project README (currently empty)
`-- filestructure.md                  # Older project layout document
```

## Main folders

| Folder | Purpose |
| --- | --- |
| `app/` | Runs the API and defines the shared data models. The active server entry point is `app.main:app`. |
| `app/providers/` | Keeps mock and Gemini extraction separate from the HTTP endpoints. |
| `data/` | Stores known inputs and expected outputs for repeatable offline testing. |
| `docs/` | Holds requirements, API examples, setup notes, and this guide. |
| `src/vaais_core/` | Contains the console-script package; its current command does not start the API. |
| `tests/` | Checks endpoint behavior, fixtures, provider selection, and output validation. Some tests still reflect earlier development stages. |

## Extraction flow

1. A client sends text to `POST /extract` in `app/main.py`.
2. `app/schemas.py` validates the request.
3. `app/providers/factory.py` reads configuration and selects mock or Gemini.
4. The endpoint runs the synchronous provider in a thread pool.
5. The provider returns an `ExtractionResponse`, or the endpoint maps a provider
   error to an HTTP error response.

The mock provider matches fixture text exactly; unmatched input returns unknown
fields with `needs_review=true`. The Gemini provider sends the inquiry with a
JSON schema and validates the resulting structured output.

Local tooling directories such as `.venv/`, `.pytest_cache/`, `__pycache__/`,
and `.git/` are omitted from the tree.
