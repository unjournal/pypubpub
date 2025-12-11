# pypubpub - PubPub API Client for The Unjournal

Python package for interacting with the PubPub v6 API (pubpub.org). Created for The Unjournal (unjournal.org) to automate the production process for evaluation packages.

## 🚀 What's New: Automated Evaluation Package Creation

**85% automation achieved!** Create complete evaluation packages in ~12 minutes (down from 2-3 hours).

### Quick Start

```python
from scripts.pubpub_automation.package_assembler import PaperMetadata, EvaluationData, EvaluationPackageData
from scripts.pubpub_automation.create_package_from_data import EvaluationPackageCreator
import conf

# 1. Define paper
paper = PaperMetadata(
    title='Your Paper Title',
    authors=['Author 1', 'Author 2'],
    doi='10.1234/example'
)

# 2. Define evaluations
evaluations = [
    EvaluationData(
        ratings={'overall_assessment': 90, 'methods': 85},
        review_source_type='latex',  # or 'markdown', 'text'
        review_source_path='/path/to/review.tex',
        evaluator_name='Jane Doe',
        is_public=False  # Anonymous for draft mode
    )
]

# 3. Create package
creator = EvaluationPackageCreator(
    email=conf.email, password=conf.password,
    community_url=conf.community_url, community_id=conf.community_id
)

package_data = EvaluationPackageData(paper=paper, evaluations=evaluations)
result = creator.create_package(package_data, draft_mode=True)

# Done! Package is live with all content automatically imported
```

### Features

✅ **Automatic LaTeX Conversion** - LaTeX reviews → markdown → PubPub
✅ **Automatic Ratings Tables** - Generate formatted tables from data
✅ **Draft/Final Workflow** - Anonymous posting → add names after consent
✅ **Template System** - Auto-filled evaluation summaries
✅ **Coda Integration** - Fetch evaluations from Coda.io (ready to test)
✅ **General Purpose** - Works for any evaluation

### Time Savings

| Task | Before | After |
|------|--------|-------|
| Convert LaTeX review | 30 min | Automatic |
| Create ratings tables | 20 min | Automatic |
| Fill templates | 20 min | Automatic |
| Import to PubPub | 20 min | Automatic |
| **Total** | **2-3 hours** | **~12 minutes** |

## 📖 Documentation

- **[AUTOMATION_COMPLETE.md](AUTOMATION_COMPLETE.md)** - Complete automation overview
- **[docs/AUTOMATION_WORKFLOW.md](docs/AUTOMATION_WORKFLOW.md)** - Detailed usage guide
- **[scripts/pubpub_automation/README.md](scripts/pubpub_automation/README.md)** - Quick reference
- **[AUTOMATION_STATUS.md](AUTOMATION_STATUS.md)** - Current capabilities (85% automated)
- **[CLAUDE.md](CLAUDE.md)** - Developer guide

## 🔧 Setup

### Installation

```bash
# Install package in development mode
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

### Coda Integration Setup

1. Create `.env` file in repository root (already templated for you)
2. Add your Coda API credentials:
   ```bash
   CODA_API_KEY=your_api_key_here
   CODA_DOC_ID=your_doc_id_here
   CODA_TABLE_ID=your_table_id_here
   ```
3. See **[docs/CODA_SETUP.md](docs/CODA_SETUP.md)** for detailed instructions

### Test Your Setup

```bash
# Check .env configuration
python scripts/coda_integration/check_env.py

# Test Coda connection (after adding API key)
python scripts/coda_integration/test_coda_connection.py

# Test LaTeX conversion
python scripts/pubpub_automation/latex_to_markdown.py input.tex output.md
```

## 📁 Project Structure

```
pypubpub/
  ├── pypubpub/              # Core API client library
  │   ├── Pubv6.py           # Main API classes (Pubshelper_v6, EvaluationPackage)
  │   ├── utils.py           # Utility functions
  │   └── repec/             # RePEc metadata generation
  │
  ├── scripts/
  │   ├── pubpub_automation/       # NEW: Automated package creation
  │   │   ├── create_package_from_data.py  # Main automation script
  │   │   ├── package_assembler.py         # Package assembly
  │   │   ├── latex_to_markdown.py         # LaTeX converter
  │   │   ├── ratings_table_generator.py   # Table generator
  │   │   └── template_generator.py        # Template system
  │   │
  │   ├── coda_integration/        # Coda.io API integration
  │   │   ├── fetch_from_coda.py   # Fetch evaluation data
  │   │   ├── setup_coda.py        # Setup wizard
  │   │   └── check_env.py         # Verify configuration
  │   │
  │   └── utilities/               # Utility scripts
  │
  ├── docs/                  # Documentation
  │   ├── AUTOMATION_WORKFLOW.md   # Complete usage guide
  │   ├── AUTOMATION_GUIDE.md      # Original guide
  │   ├── CODA_SETUP.md            # Coda setup instructions
  │   └── CODA_WORKFLOW.md         # Coda integration details
  │
  ├── examples/              # Example evaluation packages
  │   └── evaluation_packages/
  │       └── scale_use_heterogeneity/  # Working example
  │
  └── tests/                 # Test suite
```

## 🎯 Main Use Cases

### 1. Create Evaluation Package from Files

```python
# For LaTeX reviews, PDF ratings, local data
creator.create_from_files(
    paper_metadata=paper,
    evaluation_files=[...],
    draft_mode=True
)
```

### 2. Create Package from Coda (Coming Soon)

```python
# Fetch from Coda and create package
from scripts.coda_integration.fetch_from_coda import fetch_evaluation_data

coda_data = fetch_evaluation_data("Paper Title")
creator.create_from_coda(coda_data, paper_metadata)
```

### 3. Draft → Final Workflow

```python
# Step 1: Draft (anonymous)
result = creator.create_package(package_data, draft_mode=True)
# Share with authors...

# Step 2: Final (with names after consent)
for eval in evaluations:
    if evaluator_consented:
        eval.is_public = True
result = creator.create_package(package_data, draft_mode=False)
```

## 🔐 Security

- ✅ `.env` file gitignored - safe for credentials
- ✅ `conf.py` gitignored - never committed
- ✅ Sensitive evaluation data in `evaluation_data/confidential/` (gitignored)
- ✅ Comprehensive .gitignore patterns for secrets
- ⚠️ Never commit API keys or passwords
- ⚠️ Never commit evaluator pseudonyms or confidential comments

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_create/test_create_eval_package.py

# Test with verbose output
pytest -v
```

Test configuration in `tests/conf_settings.py` (copy from `tests/conf_settings_template.py`).

## 📦 Core API Components

### Pubshelper_v6

Main API client with methods for:
- `get_many_pubs()` - Query and retrieve pubs
- `create_pub()` - Create new publications
- `connect_pub()` - Link pubs together
- `set_attribution()` - Manage authors
- `replace_pub_text()` - Update content
- `downloadpubexport()` - Export in various formats

### EvaluationPackage

High-level class for creating complete evaluation packages:
- Looks up paper metadata from DOI
- Creates evaluation summary + individual evaluations
- Sets up all connections
- Associates authors/evaluators

### Automation Scripts

**NEW automated workflow:**
- Convert LaTeX/Word → Markdown
- Generate ratings tables
- Fill evaluation templates
- Import content to PubPub
- Handle draft/final modes

## 🛠️ Utility Scripts

### Evaluation Package Creation

```bash
# Create from data with automation
python scripts/pubpub_automation/create_package_from_data.py --config config.json
```

### Backup Pubs

```python
from pypubpub.scripttasks.backup import backupV6

backupV6(pubhelper=pubhelper, output_dir="./backups", format='plain')
```

### Generate RePEc Metadata

```python
from pypubpub.repec import RePEcPopulator

populator = RePEcPopulator(pubhelper=pubhelper, inputdir="./repec_rdfs")
metadata = populator.build_metadata_file()
```

## 🌐 Related Resources

- **PubPub API Docs:** https://www.pubpub.org/apiDocs
- **The Unjournal:** https://unjournal.org
- **Production Work:** https://github.com/daaronr/unjournalpubpub_production
- **Task Tracking:** https://coda.io/d/_dOyXJoZ6imx

## 📈 Project Goals

1. **Automate evaluation package creation** ✅ 85% complete
2. **Enable ad-hoc adjustments and bulk fixes** ✅ Complete
3. **Build RePEc metadata** ✅ Complete
4. **Enable feeds and updates** 🚧 In progress
5. **Coda integration** 🚧 Ready to test

## 🤝 Contributing

This is an internal tool for The Unjournal. For issues or questions:
- See documentation in `docs/`
- Check `AUTOMATION_STATUS.md` for current capabilities
- Refer to `CLAUDE.md` for development guidelines

## 📄 License

Internal project for The Unjournal.

---

**Status:** Production-ready automation system (85% automated)
**Last Updated:** December 2024
**Maintainer:** The Unjournal team
