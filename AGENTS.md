# Repository Guidelines

## Project Structure & Module Organization
- Core PubPub API helpers live in `pypubpub/` (`Pubv6.py`, `scripttasks/`, `repec/`, `utility/`); keep reusable abstractions here.
- Automation and maintenance scripts sit under `scripts/` (`pubpub_automation/` for package assembly, `utilities/` for DOI/link fixes); notebooks and exploratory work live in `notebooks/`.
- `tests/` houses pytest suites grouped by feature (`test_create/`, `test_batch_operations/`, `test_repec/`). Large production artifacts stay in `repec_rdfs/` and should not be edited unless regenerating metadata.
- Add new docs beside existing references in `docs/` (automation guides, setup summaries) so operational notes remain centralized.

## Build, Test, and Development Commands
- Create a virtual environment and install editable dependencies:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -e .[dev]
  ```
- Run the full suite (requires API creds via `tests/conf_settings.py`):
  ```bash
  pytest
  ```
- Targeted checks: `pytest tests/test_create/test_create_pub.py -k batch` for creation flows, `python scripts/utilities/delete_untitled_pubs.py` or other `scripts/pubpub_automation/*.py` entries to exercise individual tools.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, snake_case for functions, PascalCase for classes (`Pubshelper_v6`, `UserAttribution`), and descriptive module names; match the existing pattern when adding helpers (e.g., `generate_slug` in `utils.py`).
- Prefer dataclasses/TypedDicts for structured payloads and keep API payload assembly near the helper that submits it.
- Inline logging should stay human-readable; favor f-strings and avoid leaking passwords (mask as done in `login`).

## Testing Guidelines
- Pytest discovers any `test_*.py`; mirror the existing directory naming (feature folders) and keep fixtures in `tests/conftest.py`.
- Integration tests depend on live PubPub credentials stored in a developer-only `tests/conf_settings.py`; copy and edit `tests/conf_settings_template.py` and never commit secrets.
- When adding automation, provide a fast unit-style test that mocks network calls in addition to any credentialed integration case; include assertions for retries, slug generation, and cleanup.

## Commit & Pull Request Guidelines
- Recent history (`moves and cleanups`, `Add utility script to delete untitled publications`) shows concise, imperative summaries—stick to that voice and keep titles under ~50 chars.
- PRs should describe the automation or API behavior touched, reference the relevant script or module paths, list manual test commands (e.g., `pytest`, script invocations), and attach screenshots or logs when they change PubPub content.
- Link Coda tasks or GitHub issues when applicable, call out required credentials/config files, and note any doc updates made in `docs/` or `AGENTS.md`.

## Security & Configuration Tips
- Store secrets in environment variables or `.env`/`tests/conf_settings.py`; `.env.example` documents required keys.
- Scripts that call PubPub or Coda APIs assume HTTPS endpoints—double-check community IDs and avoid committing generated RDFs or evaluation drafts unless they are finalized.
