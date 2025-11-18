# Scripts Directory

Organized automation and utility scripts for pypubpub.

## Directory Structure

### `coda_integration/`
Scripts for fetching evaluation data from Coda.io

- `setup_coda.py` - Interactive wizard to configure Coda API access
- `test_coda_connection.py` - Verify Coda connection and preview data
- `fetch_from_coda.py` - Fetch evaluations, separate sensitive data

**Usage:**
```bash
# One-time setup
python scripts/coda_integration/setup_coda.py

# Test connection
python scripts/coda_integration/test_coda_connection.py

# Fetch data
python scripts/coda_integration/fetch_from_coda.py "Paper Title"
```

### `pubpub_automation/`
Scripts for creating and managing PubPub packages

- `setup_credentials.py` - Set up PubPub credentials

### `utilities/`
Helper scripts for maintenance and fixes

- `fix_*.py` - Various URL and DOI fixing scripts
- `scan_links.py` - Scan pubs for broken links
- `check_*.py` - Validation scripts
- `audit_collections.py` - Audit PubPub collections
- And more...

## Security Notes

⚠️ Never run scripts with hardcoded credentials!

All scripts should use:
- Environment variables from `.env`
- Config from `conf.py` (gitignored)
- Command-line arguments

See main [README.md](../README.md) for security guidelines.
