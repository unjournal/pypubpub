# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pypubpub is a Python package for interacting with the PubPub v6 API (pubpub.org). It was created for The Unjournal (unjournal.org) to automate their production process - primarily building "evaluation packages" which consist of evaluation summaries and individual evaluations that are linked together and connected to original research papers.

**Current Status:** 85% automation achieved. The system can now create complete evaluation packages with LaTeX conversion, ratings tables, and content import in ~12 minutes (down from 2-3 hours manual work).

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

### Automation System (NEW)

**EvaluationPackageCreator** (scripts/pubpub_automation/create_package_from_data.py:25)
- Main automation script for creating complete evaluation packages
- Orchestrates the entire workflow: data → markdown → PubPub
- Supports draft mode (anonymous) and final mode (with names)
- Key methods:
  - `create_package()` - Create complete package from structured data
  - `create_from_coda()` - Create from Coda.io form data
  - `create_from_files()` - Create from local files (LaTeX, JSON, etc.)

**PackageAssembler** (scripts/pubpub_automation/package_assembler.py:90)
- Assembles evaluation packages from various data sources
- Converts review files to markdown
- Generates complete package markdown for import
- Key methods:
  - `assemble_from_data()` - Assemble from structured EvaluationPackageData
  - `assemble_from_coda()` - Assemble from Coda API data
  - `assemble_from_files()` - Assemble from local files

**LatexToMarkdownConverter** (scripts/pubpub_automation/latex_to_markdown.py:18)
- Converts LaTeX evaluation reviews to PubPub-compatible markdown
- Handles sections, lists, citations, math, formatting
- Successfully tested with real evaluation reviews
- Key methods:
  - `convert()` - Convert LaTeX string to markdown
  - `convert_file()` - Convert LaTeX file to markdown
  - `convert_with_metadata()` - Convert and add metadata header

**RatingsTableGenerator** (scripts/pubpub_automation/ratings_table_generator.py:67)
- Generates markdown tables from evaluation ratings data
- Supports multiple formats: ranges (lower/mid/upper), numbers, strings
- Generates comparison tables for multiple evaluators
- Auto-labels standard Unjournal criteria
- Key methods:
  - `generate_ratings_table()` - Single evaluator table
  - `generate_comparison_table()` - Multi-evaluator comparison
  - `generate_summary_stats()` - Summary statistics

**TemplateGenerator** (scripts/pubpub_automation/template_generator.py:15)
- Creates evaluation summary and individual evaluation templates
- Auto-fills paper metadata and generates comparison tables
- Key methods:
  - `generate_evaluation_summary()` - Summary document with comparison table
  - `generate_individual_evaluation()` - Individual evaluation document
  - `generate_complete_package()` - Complete package (summary + all evaluations)

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

### Creating Evaluation Packages (Legacy Method)

Original method using EvaluationPackage class (creates structure only, no content):

```python
from pypubpub import Pubshelper_v6
from pypubpub.Pubv6 import EvaluationPackage

# Create an evaluation package structure (will auto-execute by default)
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

### Creating Evaluation Packages (NEW Automated Method)

**Recommended:** Use the automated system for complete packages with content:

```python
from scripts.pubpub_automation.package_assembler import (
    PaperMetadata, EvaluationData, EvaluationPackageData
)
from scripts.pubpub_automation.create_package_from_data import EvaluationPackageCreator
import conf

# Define paper metadata
paper = PaperMetadata(
    title='Paper Title',
    authors=['Author 1', 'Author 2'],
    doi='10.1234/example'
)

# Define evaluations with ratings and review files
evaluations = [
    EvaluationData(
        ratings={
            'overall_assessment': {'lower': 80, 'mid': 90, 'upper': 100},
            'methods': 85,
            # ... other criteria
        },
        review_source_type='latex',  # or 'markdown', 'text'
        review_source_path='/path/to/review.tex',
        evaluator_name='Jane Doe',
        evaluator_affiliation='University X',
        evaluator_orcid='0000-0000-0000-0000',
        is_public=False  # Set to True after evaluator consents
    ),
    # ... more evaluations
]

# Create package
creator = EvaluationPackageCreator(
    email=conf.email,
    password=conf.password,
    community_url=conf.community_url,
    community_id=conf.community_id
)

package_data = EvaluationPackageData(
    paper=paper,
    evaluations=evaluations,
    manager_summary="Brief summary of the evaluations..."
)

# Create in draft mode (anonymous)
result = creator.create_package(package_data, draft_mode=True)

# This creates:
# - Evaluation summary pub WITH comparison table
# - Individual evaluation pubs WITH converted content and ratings tables
# - All connections set up
# - Everything ready to share with authors

# After author response and evaluator consent, update and re-run:
for eval in evaluations:
    if evaluator_consented:
        eval.is_public = True

result = creator.create_package(package_data, draft_mode=False)
# Now includes evaluator names
```

**Key differences:**
- Legacy method: Creates empty pubs, manual content import needed
- Automated method: Creates pubs WITH all content automatically imported
- Automated method: Handles LaTeX conversion, table generation, templates
- Automated method: Supports draft/final workflow

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
  ├── pypubpub/              # Core API client library
  │   ├── __init__.py        # Package entry point, exports Pubshelper_v6
  │   ├── Pubv6.py           # Main API client and high-level classes
  │   ├── utils.py           # Utility functions (retry, slugify, etc.)
  │   ├── utility/
  │   │   ├── __init__.py    # Titlemachine class
  │   │   └── people.py      # Known PubPub user IDs
  │   ├── repec/
  │   │   └── __init__.py    # RePEcPopulator for RePEc metadata
  │   └── scripttasks/
  │       ├── backup.py      # Backup functionality
  │       ├── export.py      # Export functionality
  │       └── repec-rdf-bulder.py # Script for building RePEc files
  │
  ├── scripts/                        # NEW: Automation scripts
  │   ├── pubpub_automation/          # Automated package creation
  │   │   ├── create_package_from_data.py  # Main automation script
  │   │   ├── package_assembler.py         # Package assembly
  │   │   ├── latex_to_markdown.py         # LaTeX converter
  │   │   ├── ratings_table_generator.py   # Table generator
  │   │   ├── template_generator.py        # Template system
  │   │   └── README.md                    # Quick reference
  │   │
  │   ├── coda_integration/           # Coda.io API integration
  │   │   ├── fetch_from_coda.py      # Fetch evaluation data
  │   │   ├── setup_coda.py           # Setup wizard
  │   │   ├── test_coda_connection.py # Connection verification
  │   │   └── check_env.py            # Verify .env configuration
  │   │
  │   └── utilities/                  # Utility scripts
  │
  ├── docs/                           # Documentation
  │   ├── AUTOMATION_WORKFLOW.md      # Complete usage guide
  │   ├── AUTOMATION_GUIDE.md         # Original guide
  │   ├── CODA_SETUP.md               # Coda setup instructions
  │   └── CODA_WORKFLOW.md            # Coda integration details
  │
  ├── examples/                       # Example evaluation packages
  │   ├── evaluation_packages/
  │   │   └── scale_use_heterogeneity/  # Working example with Caspar & Prati
  │   └── templates_and_example_pubs_md/ # PubPub templates and examples
  │
  ├── tests/                          # Test suite
  │   ├── conf_settings.py            # Test configuration (not in repo)
  │   ├── conf_settings_template.py   # Template for test config
  │   ├── conftest.py                 # Pytest fixtures
  │   ├── test_create/                # Tests for pub creation
  │   ├── test_batch_operations/      # Tests for batch operations
  │   └── test_repec/                 # Tests for RePEc functionality
  │
  ├── repec_rdfs/                     # Generated RePEc metadata files
  ├── notebooks/                      # Jupyter notebooks for experimentation
  │
  ├── .env                            # Coda API credentials (gitignored, not committed)
  ├── .env.example                    # Template for .env file
  ├── AUTOMATION_COMPLETE.md          # Complete automation overview
  ├── AUTOMATION_STATUS.md            # Current capabilities (85% automated)
  └── README.md                       # Main project documentation
```

## Coda Integration Setup

### Environment Variables

Coda integration requires a `.env` file in the repository root with:

```bash
CODA_API_KEY=your_api_key_here
CODA_DOC_ID=your_doc_id_here
CODA_TABLE_ID=your_table_id_here
```

### Getting Credentials

1. **API Key:** Go to https://coda.io/account → API Settings → Generate token
2. **Document ID:** From URL `https://coda.io/d/_dXXXXXXX` → Copy the `_dXXXXXXX` part
3. **Table ID:** Use `python scripts/coda_integration/setup_coda.py` to find table IDs

### Verify Setup

```bash
# Check .env configuration
python scripts/coda_integration/check_env.py

# Test connection
python scripts/coda_integration/test_coda_connection.py
```

See **docs/CODA_SETUP.md** for detailed instructions.

## Automation Quick Reference

### Create Package from Files

```python
from scripts.pubpub_automation.create_package_from_data import EvaluationPackageCreator
from scripts.pubpub_automation.package_assembler import PaperMetadata, EvaluationData, EvaluationPackageData
import conf

creator = EvaluationPackageCreator(
    email=conf.email, password=conf.password,
    community_url=conf.community_url, community_id=conf.community_id
)

package_data = EvaluationPackageData(
    paper=PaperMetadata(title='...', authors=['...'], doi='...'),
    evaluations=[
        EvaluationData(
            ratings={'overall_assessment': 90, ...},
            review_source_path='/path/to/review.tex',
            review_source_type='latex',
            evaluator_name='...',
            is_public=False
        )
    ]
)

result = creator.create_package(package_data, draft_mode=True)
```

### Key Features

- ✅ **85% automation** - ~12 minutes vs 2-3 hours
- ✅ **LaTeX conversion** - Automatic with tested converter
- ✅ **Ratings tables** - Auto-generated from data
- ✅ **Draft/final modes** - Anonymous → with names
- ✅ **Template system** - Auto-filled summaries
- ⚠️ **Coda integration** - Ready to test with credentials

### Documentation

- **AUTOMATION_COMPLETE.md** - Complete overview
- **docs/AUTOMATION_WORKFLOW.md** - Usage guide
- **scripts/pubpub_automation/README.md** - Quick reference
- **AUTOMATION_STATUS.md** - Current capabilities

## Related Resources

- PubPub API Documentation: https://www.pubpub.org/apiDocs
- The Unjournal: https://unjournal.org
- Production work repository: https://github.com/daaronr/unjournalpubpub_production
- Coda task tracking: https://coda.io/d/_dOyXJoZ6imx#All-unfinished-current-Tasks_tuXFw
