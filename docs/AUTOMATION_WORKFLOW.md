# Evaluation Package Automation Workflow

Complete guide to creating evaluation packages automatically.

## Overview

The automation system converts evaluation data (from Coda, LaTeX, PDFs, etc.) into markdown, then creates and populates PubPub packages automatically.

## Architecture

```
Data Sources          Conversion           PubPub
┌─────────────┐      ┌────────────┐      ┌──────────────┐
│ Coda Forms  │──┐   │  Markdown  │      │  Pub Package │
│ LaTeX Files │──┼──→│ Generation │─────→│ + Content    │
│ PDF Ratings │──┘   │            │      │ + Metadata   │
└─────────────┘      └────────────┘      └──────────────┘
```

### Components

1. **`latex_to_markdown.py`** - Converts LaTeX reviews to markdown
2. **`ratings_table_generator.py`** - Creates markdown tables from ratings data
3. **`template_generator.py`** - Generates evaluation summary and individual evaluation templates
4. **`package_assembler.py`** - Assembles complete packages from various sources
5. **`create_package_from_data.py`** - Main script that creates PubPub packages with content

## Quick Start

### Option 1: From Local Files (Recommended for Testing)

```python
from package_assembler import PaperMetadata, EvaluationData
from create_package_from_data import EvaluationPackageCreator
import conf  # Your credentials

# 1. Define paper
paper = PaperMetadata(
    title='Your Paper Title',
    authors=['Author 1', 'Author 2'],
    doi='10.1234/example'
)

# 2. Define evaluations
evaluations = [
    EvaluationData(
        ratings={
            'overall_assessment': {'lower': 80, 'mid': 90, 'upper': 100},
            'methods': 85,  # Can be simple numbers
        },
        evaluator_name='Jane Doe',
        is_public=False,  # Anonymous for draft
        review_source_type='latex',
        review_source_path='/path/to/review.tex'
    )
]

# 3. Create package
creator = EvaluationPackageCreator(
    email=conf.email,
    password=conf.password,
    community_url=conf.community_url,
    community_id=conf.community_id
)

from package_assembler import EvaluationPackageData

package_data = EvaluationPackageData(
    paper=paper,
    evaluations=evaluations,
    manager_summary="Brief summary of the evaluations..."
)

result = creator.create_package(
    package_data=package_data,
    draft_mode=True,  # Don't add evaluator names yet
    output_dir='/tmp/my_package'
)
```

### Option 2: From JSON Config

```bash
# Create config file
cat > config.json << 'EOF'
{
  "pubpub": {
    "email": "your@email.com",
    "password": "your_password",
    "community_url": "https://unjournal.pubpub.org",
    "community_id": "d28e8e57-7f59-486b-9395-b548158a27d6"
  },
  "paper": {
    "title": "Your Paper Title",
    "authors": ["Author 1", "Author 2"],
    "doi": "10.1234/example"
  },
  "evaluations": [
    {
      "ratings": {
        "overall_assessment": {"lower": 80, "mid": 90, "upper": 100},
        "methods": 85
      },
      "review": "/path/to/review.tex",
      "evaluator_name": "Jane Doe",
      "is_public": false
    }
  ],
  "manager_summary": "Brief summary..."
}
EOF

# Run automation
python scripts/pubpub_automation/create_package_from_data.py \
  --config config.json \
  --draft \
  --output-dir /tmp/package_output
```

### Option 3: From Coda (Future)

```python
# Fetch from Coda
from scripts.coda_integration.fetch_from_coda import fetch_evaluation_data

coda_data = fetch_evaluation_data(paper_title="Your Paper")

# Create package
result = creator.create_from_coda(
    coda_data=coda_data,
    paper_metadata=paper,
    draft_mode=True
)
```

## Workflow: Draft → Final

### 1. Draft Mode (Initial Posting)

```python
# Create anonymous package for author response
result = creator.create_package(
    package_data=package_data,
    draft_mode=True  # No evaluator names
)
```

**Draft mode:**
- ✓ Creates package structure
- ✓ Imports all content (reviews, ratings, tables)
- ✓ Sets up connections
- ✗ Does NOT add evaluator names (anonymous)

**Use for:**
- Initial posting before author response
- When evaluators haven't consented to identification yet

### 2. Final Mode (After Author Response)

```python
# Update evaluations with public status
for evaluation in evaluations:
    if evaluator_consented:
        evaluation.is_public = True

# Re-create or update package
result = creator.create_package(
    package_data=package_data,
    draft_mode=False  # Add names
)
```

**Final mode:**
- ✓ Adds evaluator names (for those who consented)
- ✓ Adds ORCID, affiliation
- ✓ Ready for DOI request

## Data Structure Reference

### PaperMetadata

```python
PaperMetadata(
    title: str,                    # Required
    authors: List[str] | str,      # Required
    doi: Optional[str] = None,     # Preferred
    url: Optional[str] = None,     # If no DOI
    abstract: Optional[str] = None,
    year: Optional[int] = None
)
```

### EvaluationData

```python
EvaluationData(
    ratings: Dict[str, Dict | float | int | str],  # Required
    review_text: Optional[str] = None,              # Or use source file

    # Evaluator info (only shown if is_public=True)
    evaluator_name: Optional[str] = None,
    evaluator_affiliation: Optional[str] = None,
    evaluator_orcid: Optional[str] = None,
    is_public: bool = False,  # Show name?

    # Source file for review
    review_source_type: Optional[str] = None,  # 'latex', 'word', 'markdown', 'text'
    review_source_path: Optional[Path] = None,

    comments: Optional[str] = None
)
```

### Ratings Format

Ratings can be in multiple formats:

```python
ratings = {
    # Format 1: Dict with range
    'overall_assessment': {'lower': 80, 'mid': 90, 'upper': 100},

    # Format 2: Simple number
    'methods': 85,

    # Format 3: String (parsed automatically)
    'logic_communication': '80 (70-90)',

    # Standard criteria (auto-labeled):
    'overall_assessment',
    'advancing_knowledge',
    'methods',
    'logic_communication',
    'open_collaborative',
    'real_world_relevance',
    'relevance_to_global_priorities',
    'journal_merit',
    'claims_evidence',

    # Custom criteria also supported
    'custom_criterion': 75
}
```

## Converting Review Files

### LaTeX to Markdown

The system automatically converts LaTeX:

```python
# Automatic conversion when using review_source_path
evaluation = EvaluationData(
    ratings=...,
    review_source_type='latex',
    review_source_path='/path/to/review.tex'
)
```

Or manually:

```bash
python scripts/pubpub_automation/latex_to_markdown.py input.tex output.md
```

**Supported LaTeX features:**
- Sections: `\section`, `\subsection`, `\subsubsection`
- Formatting: `\textbf`, `\textit`, `\emph`, `\texttt`
- Lists: `\begin{enumerate}`, `\begin{itemize}`
- Math: Inline `$...$`, display `$$...$$`, `\[...\]`
- Citations: `\cite{key}` → `[key]`

### Word to Markdown

**Option 1: Pandoc (Recommended)**

```bash
pandoc review.docx -o review.md
```

**Option 2: Manual conversion** (then use markdown source)

### PDF Ratings Extraction

Currently manual - use the PDF to extract ratings into JSON/dict format.

## Complete Example

See `examples/evaluation_packages/scale_use_heterogeneity/create_package_automated.py` for a real-world example with:
- LaTeX review conversion
- Multiple evaluators
- Draft/final modes
- All metadata and connections

## Output

The automation creates:

1. **PubPub Publications:**
   - Evaluation summary pub (with comparison table)
   - Individual evaluation pubs (one per evaluator)
   - All connections set up
   - All content imported

2. **Markdown Files** (if output_dir specified):
   - `evaluation_summary.md`
   - `evaluation_1.md`, `evaluation_2.md`, etc.

3. **Return Value:**
   ```python
   {
       'summary_pub_id': '...',
       'summary_slug': '...',
       'evaluation_pubs': [
           {'id': '...', 'slug': '...'},
           ...
       ],
       'package_markdown': {
           'summary': '...',
           'evaluations': ['...', '...']
       }
   }
   ```

## Troubleshooting

### LaTeX Conversion Issues

- **Complex LaTeX:** Simplify or manually convert to markdown
- **Custom commands:** Define in `latex_to_markdown.py` or preprocess
- **Bibliography:** References converted to `[citation_key]` - may need manual formatting

### Import Errors

- Check that file paths are absolute
- Ensure credentials are correct
- Verify PubPub community access

### Missing Ratings

- Ensure ratings dict has at least one entry
- Check field names match standard criteria or use custom names

## Next Steps

1. **Test with example:** Run `create_package_automated.py`
2. **Prepare your data:** Gather ratings, reviews, paper metadata
3. **Run in draft mode:** Create anonymous package
4. **Share with authors:** Get author response
5. **Run in final mode:** Add evaluator names if consented
6. **Request DOIs:** Use PubPub API to request DOIs

## See Also

- `AUTOMATION_STATUS.md` - Current automation capabilities
- `CODA_WORKFLOW.md` - Coda integration guide
- `SETUP_SUMMARY.md` - Setup instructions
