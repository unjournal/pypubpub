# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pypubpub is a Python package for interacting with the PubPub v6 API (pubpub.org). It was created for The Unjournal (unjournal.org) to automate their production process - primarily building "evaluation packages" which consist of evaluation summaries and individual evaluations that are linked together and connected to original research papers.

## Key Architecture

### Core Classes

**Pubshelper_v6** (pypubpub/Pubv6.py:45)
- Main API client for PubPub v6
- Handles authentication via login() using keccak-512 hashed passwords
- Provides methods for CRUD operations on pubs (publications)
- Key methods:
  - `get_many_pubs()` - Query and retrieve multiple pubs with filtering
  - `create_pub()` - Create new pubs with slug, title, description
  - `delete_pub()` / `batch_delete()` - Delete single or multiple pubs
  - `connect_pub()` / `connect_pub_to_external()` - Link pubs together or to external resources
  - `set_attribution()` / `set_attributions_multiple()` - Manage authors/contributors
  - `update_pub()` - Update pub metadata
  - `replace_pub_text()` - Replace pub content
  - `downloadpubexport()` - Export pubs in various formats (plain, html, pdf, etc.)

**Migratehelper_v6** (pypubpub/Pubv6.py:669)
- High-level wrapper around Pubshelper_v6
- Creates and manipulates v6 Pubs with simplified interfaces
- Methods for creating connected pub structures

**EvaluationPackage** (pypubpub/Pubv6.py:952)
- High-level class for creating complete evaluation packages
- Automates the process of:
  1. Looking up parent paper metadata via DOI or URL (using doi.org and CrossRef)
  2. Creating evaluation summary pub and individual evaluation pubs
  3. Linking all pubs together
  4. Associating authors/evaluators
  5. Copying template content into new pubs
- Key parameters:
  - `doi` - DOI of parent paper to evaluate
  - `url` - URL if DOI not available
  - `evaluation_manager_author` - User ID or name
  - `evaluations` - List of evaluation configs (can specify authors or leave empty)
  - `autorun` - Whether to execute immediately (default True)

**OrigPaperMetadata** (pypubpub/Pubv6.py:820)
- Handles metadata lookup for parent papers
- Queries doi.org for BibTeX and CrossRef for JSON metadata
- Extracts title, authors, dates from external sources

**RePEcPopulator** (pypubpub/repec/__init__.py:10)
- Generates RePEc.org metadata (ReDIF format) from PubPub pubs
- Filters out template pubs and admin entries
- Handles numbering scheme for RePEc records

### Utilities

**pypubpub/utils.py**
- `retry()` - Decorator for retrying failed API calls
- `generate_slug()` - Creates URL-friendly slugs from titles (removes stopwords)
- `isMaybePubId()` - Validates if string looks like a PubPub ID (32 hex chars)
- `generate_random_number_string()` - For unique slug suffixes

**pypubpub/utility/__init__.py**
- `Titlemachine` - Generates numbered evaluation titles like "Evaluation 1 of {paper}"

**pypubpub/utility/people.py**
- Contains PubPub user IDs for known authors/evaluators

### Data Types

**UserAttribution** / **UserAttributeDict** (pypubpub/Pubv6.py:26-42)
- Used for associating authors/contributors with pubs
- Fields: userId, roles, affiliation, isAuthor, orcid, name

## Common Development Tasks

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_create/test_create_eval_package.py

# Run with verbose output
pytest -v
```

Tests use pytest with `--import-mode=importlib` (configured in pyproject.toml).

### Test Configuration

Tests require configuration in `tests/conf_settings.py` (not committed to repo). Copy `tests/conf_settings_template.py` and fill in:
- `community_url` - PubPub community URL (e.g., "https://testabcd123456789.pubpub.org")
- `community_id` - UUID of the community
- `email` - Login email
- `password` - Login password

### Installing Dependencies

```bash
# Install package in development mode
pip install -e .

# Install with dev dependencies (includes pytest)
pip install -e ".[dev]"

# Or install from requirements.txt
pip install -r requirements.txt
```

### Building Package

The package uses flit for building:

```bash
# Build package
flit build

# Install locally
flit install
```

### Creating Evaluation Packages

Example usage of the main workflow:

```python
from pypubpub import Pubshelper_v6
from pypubpub.Pubv6 import EvaluationPackage

# Create an evaluation package (will auto-execute by default)
pkg = EvaluationPackage(
    doi="10.1038/s41586-021-03402-5",
    evaluation_manager_author="37a457a9-4df7-4fd8-bbfd-baa72f0e2ab8",
    evaluations=[
        "87999afb-d603-4871-947a-d8da5e6478de",  # Just a user ID
        {"author": {"id": "7cc59a64-2673-4097-8e49-510b3202364a"}},
        {},  # Placeholder, add author later
    ],
    email="your@email.com",
    password="your_password",
    community_id="d28e8e57-7f59-486b-9395-b548158a27d6",
    community_url="https://unjournal.pubpub.org",
    autorun=True  # Set to False to prepare without executing
)

# Access created pubs
print(pkg.eval_summ_pub)  # Evaluation summary pub
print(pkg.activePubs)  # List of individual evaluation pubs
```

### Backing Up Pubs

```python
from pypubpub.scripttasks.backup import backupV6

# Backup all pubs to text files
backupV6(
    pubhelper=pubhelper,
    output_dir="./backups",
    format='plain',
    one_file=True  # Combines all into one file
)
```

### Generating RePEc Metadata

```python
from pypubpub.repec import RePEcPopulator

populator = RePEcPopulator(
    pubhelper=pubhelper,
    inputdir="./repec_rdfs",
    outputdir="./repec_rdfs",
    blacklist=[{"slug": "template-pub"}]
)

metadata = populator.build_metadata_file()
```

## Important Notes

### Authentication
- PubPub uses keccak-512 hashing for passwords (not standard bcrypt/sha256)
- Login creates a session with cookies stored in `pubhelper.cookieJar`
- Always call `login()` before making authenticated requests

### Pub Relationships
- Pubs can be linked with various relation types: "supplement", "review", etc.
- `pubIsParent` determines hierarchy direction
- External publications get auto-assigned PubPub IDs when first linked

### Batch Operations
- `batch_delete()` processes in chunks of 5 to avoid 500 errors
- Uses ThreadPoolExecutor for parallel deletion
- Always prefer `batch_delete()` over `delete_many_pubs()`

### Retry Logic
- Network operations should use the `@retry()` decorator
- Default is 3 retries with 2-second sleep between attempts
- Critical for reliability with PubPub API

### Slug Generation
- Slugs are URL-safe, lowercase, hyphenated strings
- Stopwords are removed by default
- Random 4-digit suffix added to ensure uniqueness

## Project Structure

```
pypubpub/
  __init__.py           # Package entry point, exports Pubshelper_v6
  Pubv6.py              # Main API client and high-level classes
  utils.py              # Utility functions (retry, slugify, etc.)
  utility/
    __init__.py         # Titlemachine class
    people.py           # Known PubPub user IDs
  repec/
    __init__.py         # RePEcPopulator for RePEc metadata
  scripttasks/
    backup.py           # Backup functionality
    export.py           # Export functionality
    repec-rdf-bulder.py # Script for building RePEc files

tests/
  conf_settings.py           # Test configuration (not in repo)
  conf_settings_template.py  # Template for test config
  conftest.py                # Pytest fixtures
  test_create/               # Tests for pub creation
  test_batch_operations/     # Tests for batch operations
  test_repec/                # Tests for RePEc functionality

repec_rdfs/             # Generated RePEc metadata files
notebooks/              # Jupyter notebooks for experimentation
```

## Related Resources

- PubPub API Documentation: https://www.pubpub.org/apiDocs
- The Unjournal: https://unjournal.org
- Production work repository: https://github.com/daaronr/unjournalpubpub_production
- Coda task tracking: https://coda.io/d/_dOyXJoZ6imx#All-unfinished-current-Tasks_tuXFw
