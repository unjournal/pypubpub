# Repository Reorganization Plan

## Current Issues
- Root directory cluttered with 50+ files
- Mix of utilities, documentation, and one-off scripts
- Credentials in `conf.py` (gitignored but risky)
- No clear structure for automation vs utilities

## Proposed Structure

```
pypubpub/
├── pypubpub/                    # Main package (existing)
│   ├── __init__.py
│   ├── Pubv6.py
│   └── utils.py
│
├── scripts/                     # Automation scripts
│   ├── coda_integration/
│   │   ├── fetch_from_coda.py
│   │   ├── setup_coda.py
│   │   └── test_coda_connection.py
│   │
│   ├── pubpub_automation/
│   │   ├── create_eval_package.py
│   │   └── setup_credentials.py
│   │
│   └── utilities/
│       ├── fix_backslash_urls.py
│       ├── fix_doi_periods.py
│       ├── scan_links.py
│       └── ... (other utility scripts)
│
├── docs/                        # Documentation
│   ├── AUTOMATION_GUIDE.md
│   ├── CODA_WORKFLOW.md
│   ├── CODA_SETUP_GUIDE.md
│   ├── QUICKSTART_CODA.md
│   └── SETUP_SUMMARY.md
│
├── examples/                    # Example scripts
│   ├── evaluation_packages/
│   │   └── scale_use_heterogeneity/
│   │       ├── create_package.py
│   │       └── README.md
│   └── README.md
│
├── evaluation_data/             # Data (GITIGNORED)
│   ├── public/                  # Safe to commit
│   └── confidential/            # NEVER commit
│
├── tests/                       # Tests (existing)
│
├── unjournalpubpub_production_moved/  # Keep as is
│   └── conf.py                  # GITIGNORED
│
├── .env                         # GITIGNORED - Coda/API keys
├── .env.example                 # Safe template
├── .gitignore                   # Updated
├── README.md                    # Clear overview
├── CLAUDE.md                    # Project guide
└── requirements.txt

```

## File Movements

### Scripts to Move

**Coda Integration:**
- `fetch_from_coda.py` → `scripts/coda_integration/`
- `setup_coda.py` → `scripts/coda_integration/`
- `test_coda_connection.py` → `scripts/coda_integration/`

**PubPub Automation:**
- `create_eval_scale_use.py` → `examples/evaluation_packages/scale_use_heterogeneity/`
- `setup_credentials.py` → `scripts/pubpub_automation/`
- `extract_prati_ratings.py` → `examples/evaluation_packages/scale_use_heterogeneity/`
- `extract_pdf_ratings.py` → `examples/evaluation_packages/scale_use_heterogeneity/`

**Utilities:**
- `fix_*.py` → `scripts/utilities/`
- `scan_links.py` → `scripts/utilities/`
- `check_*.py` → `scripts/utilities/`
- `add_to_collection.py` → `scripts/utilities/`
- `audit_collections.py` → `scripts/utilities/`
- `delete_untitled_pubs.py` → `scripts/utilities/`
- `restore_dois*.py` → `scripts/utilities/`
- `test_*.py` (non-pytest) → `scripts/utilities/`

**Documentation:**
- `AUTOMATION_GUIDE.md` → `docs/`
- `CODA_WORKFLOW.md` → `docs/`
- `SETUP_SUMMARY.md` → `docs/`
- `FIXING_BACKSLASHES_GUIDE.md` → `docs/`
- `QUICKSTART_FIX_BACKSLASHES.md` → `docs/`
- `*_REPORT.md` → `docs/reports/` (or delete if not needed)
- `README_LINK_FIXES.md` → `docs/`

### Files to Keep in Root
- `README.md` - Main project overview
- `CLAUDE.md` - Project guide for Claude
- `.gitignore`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`
- `LICENSE`

### Files to Delete (After Review)
- JSON reports (move to evaluation_data/public or delete)
- `scan_output.log`
- One-off test scripts

## Security Checklist

Before committing:
- [x] Verify `conf.py` is gitignored
- [x] Verify `.env` is gitignored
- [x] Verify `evaluation_data/confidential/` is gitignored
- [ ] Create `.env.example` without real secrets
- [ ] Remove any hardcoded API keys/passwords from scripts
- [ ] Add security warning to README
- [ ] Update all scripts to use environment variables

## Implementation Steps

1. Create directory structure
2. Move files to new locations
3. Update import paths in moved scripts
4. Update .gitignore with additional patterns
5. Create new README
6. Test that automation still works
7. Commit changes

## Notes

- Keep `unjournalpubpub_production_moved/` as-is (legacy)
- `conf.py` must NEVER be committed (already gitignored)
- All credentials must be in `.env` or environment variables
- No real API keys in any committed code
