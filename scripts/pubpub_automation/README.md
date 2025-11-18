## PubPub Automation Scripts

Automated creation of evaluation packages for The Unjournal.

## Overview

This automation system:
1. Converts evaluation reviews (LaTeX, Word, etc.) to markdown
2. Generates ratings tables from structured data
3. Creates evaluation summary and individual evaluation documents
4. Creates PubPub package structure
5. Imports all content automatically

## Quick Start

```python
from package_assembler import PaperMetadata, EvaluationData, EvaluationPackageData
from create_package_from_data import EvaluationPackageCreator
import conf  # Your credentials

# Define paper and evaluations
paper = PaperMetadata(
    title='Your Paper Title',
    authors=['Author 1', 'Author 2'],
    doi='10.1234/example'
)

evaluations = [
    EvaluationData(
        ratings={'overall_assessment': 90, 'methods': 85},
        review_source_type='latex',
        review_source_path='/path/to/review.tex',
        evaluator_name='Jane Doe',
        is_public=False  # Anonymous for draft mode
    )
]

# Create package
creator = EvaluationPackageCreator(
    email=conf.email,
    password=conf.password,
    community_url=conf.community_url,
    community_id=conf.community_id
)

package_data = EvaluationPackageData(paper=paper, evaluations=evaluations)
result = creator.create_package(package_data, draft_mode=True)
```

## Scripts

### Core Automation

- **`create_package_from_data.py`** - Main automation script
  - Creates complete PubPub packages with content
  - Supports draft mode (anonymous) and final mode (with names)
  - Can run from Python API or command line with JSON config

- **`package_assembler.py`** - Assembles packages from various sources
  - Combines data from Coda, files, manual entry
  - Converts reviews to markdown
  - Generates templates

### Converters and Generators

- **`latex_to_markdown.py`** - LaTeX to markdown converter
  - Handles sections, lists, citations, math, formatting
  - Tested with real evaluation reviews
  - Command line: `python latex_to_markdown.py input.tex output.md`

- **`ratings_table_generator.py`** - Creates markdown tables
  - Supports ranges (lower/mid/upper), simple numbers, strings
  - Generates comparison tables for multiple evaluators
  - Auto-labels standard Unjournal criteria

- **`template_generator.py`** - Template system
  - Evaluation summary templates (with comparison tables)
  - Individual evaluation templates (with ratings + review)
  - Customizable for any paper

### Utilities

- **`setup_credentials.py`** - Set up PubPub credentials (legacy)

## Workflow: Draft → Final Mode

### Draft Mode (Initial Posting)

Share evaluation with authors **before** revealing evaluator identities:

```python
result = creator.create_package(package_data, draft_mode=True)
```

Creates:
- ✓ Package structure
- ✓ All content (reviews, ratings, tables)
- ✓ All connections
- ✗ No evaluator names (anonymous)

### Final Mode (After Author Response)

After authors respond and evaluators consent to be identified:

```python
# Update evaluations
for evaluation in evaluations:
    if evaluator_consented:
        evaluation.is_public = True

# Re-create with names
result = creator.create_package(package_data, draft_mode=False)
```

Creates:
- ✓ Same as draft mode
- ✓ Adds evaluator names (if consented)
- ✓ Adds ORCID, affiliation
- ✓ Ready for DOI

## Data Formats

### Supported Review Formats

- **LaTeX** (`.tex`) - Auto-converted to markdown
- **Markdown** (`.md`) - Used directly
- **Text** (`.txt`) - Used directly
- **Word** (`.docx`) - Use pandoc to convert first

### Ratings Format

```python
ratings = {
    # Format 1: Range
    'overall_assessment': {'lower': 80, 'mid': 90, 'upper': 100},

    # Format 2: Number
    'methods': 85,

    # Format 3: String (auto-parsed)
    'logic_communication': '80 (70-90)',
}
```

### Standard Criteria

Auto-labeled in tables:
- `overall_assessment`
- `advancing_knowledge`
- `methods`
- `logic_communication`
- `open_collaborative`
- `real_world_relevance`
- `relevance_to_global_priorities`
- `journal_merit`
- `claims_evidence`

Custom criteria also supported.

## Examples

See `examples/evaluation_packages/scale_use_heterogeneity/create_package_automated.py` for complete working example.

## Output

Creates:
1. **PubPub pubs** - Summary + individual evaluations, all connected
2. **Markdown files** - Saved to output_dir if specified
3. **Return value** - Dict with pub IDs and slugs

## Requirements

```bash
pip install pypubpub
```

All conversion tools included, no external dependencies needed (except pandoc for Word files).

## Documentation

See `docs/AUTOMATION_WORKFLOW.md` for complete guide.

## Testing

```bash
# Test LaTeX conversion
python latex_to_markdown.py /tmp/review_data/main.tex /tmp/output.md

# Test ratings table
python ratings_table_generator.py

# Test template generation
python template_generator.py

# Test package assembly
python package_assembler.py
```

## Integration with Coda

See `scripts/coda_integration/` for fetching evaluation data from Coda.io.

Future integration will allow:
```python
coda_data = fetch_evaluation_data("Paper Title")
result = creator.create_from_coda(coda_data, paper_metadata)
```

## Security

- Never commit credentials
- Use `conf.py` (gitignored) or environment variables
- Keep evaluation data in `evaluation_data/confidential/` (gitignored)
- See main README.md for security guidelines
