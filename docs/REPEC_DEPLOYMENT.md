# RePEc Deployment Guide

Complete guide for generating and deploying RePEc RDF files for The Unjournal evaluations.

## Quick Start

```bash
# 1. Generate RDF files from PubPub
venv/bin/python -c "
from pypubpub.repec import RePEcPopulator
from pypubpub import Pubshelper_v6
import conf

helper = Pubshelper_v6(conf.email, conf.password, conf.community_url, conf.community_id)
helper.login()

populator = RePEcPopulator(helper, './repec_rdfs', './repec_rdfs')
populator.build_metadata_file()
"

# 2. Extract recent records (e.g., 2025 Q4)
# Edit the script to extract the range you need

# 3. Enrich with abstracts from PubPub
venv/bin/python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_04.rdf --output repec_rdfs/eval2025_04_temp.rdf

# 4. Clean Unicode and add placeholders
venv/bin/python scripts/clean_repec_rdf.py repec_rdfs/eval2025_04_temp.rdf repec_rdfs/eval2025_04.rdf

# 5. Deploy to Linode server
./scripts/deploy_repec_rdf.sh repec_rdfs/eval2025_04.rdf
```

## File Naming Convention

RePEc files follow a quarterly naming pattern:

- `eval2024_01.rdf` - Q1 2024 (Jan-Mar)
- `eval2024_02.rdf` - Q2 2024 (Apr-Jun)
- `eval2024_03.rdf` - Q3 2024 (Jul-Sep)  
- `eval2024_04.rdf` - Q4 2024 (Oct-Dec)
- `eval2025_01.rdf` - Q1 2025 (Jan-Mar)
- etc.

## Record Numbering

Records are numbered sequentially:
- Format: `2025-XX` where XX increments for each new evaluation
- Example: 2025-47, 2025-48, 2025-49, etc.

To find the next available number, check the latest deployed file or query PubPub.

## Abstract Types

### Real Abstracts (Preferred)
Extracted from "Abstract" heading on PubPub pages:
- Individual evaluations (e1*, e2*)
- Some evaluation summaries
- Some author responses

### Placeholder Abstracts (When No Abstract Exists)

**For Evaluations:**
```
This is an evaluation of the paper "PAPER TITLE" for The Unjournal. Please see the discussion below.
```

**For Author Responses:**
```
This is an author response to the Unjournal's evaluation(s) of the paper "PAPER TITLE". Please see the discussion below.
```

## Scripts

### 1. enrich_repec_abstracts.py
Extracts abstracts from PubPub pages.

**Usage:**
```bash
venv/bin/python scripts/enrich_repec_abstracts.py <input.rdf> --output <output.rdf> [--limit N]
```

**What it does:**
- Fetches each evaluation page from PubPub
- Searches for "Abstract" heading (h1/h2/h3)
- Extracts paragraphs until next heading
- Rate limited (2 second delay between requests)

### 2. clean_repec_rdf.py
Fixes Unicode issues and adds placeholders.

**Usage:**
```bash
venv/bin/python scripts/clean_repec_rdf.py <input.rdf> [output.rdf]
```

**What it does:**
- Converts all Unicode to ASCII (â→', â→", etc.)
- Adds placeholder abstracts where missing
- Detects author responses vs evaluations
- Outputs pure ASCII file

### 3. deploy_repec_rdf.sh
Deploys to Linode server with backup.

**Usage:**
```bash
./scripts/deploy_repec_rdf.sh <rdf_file> [server]
```

**What it does:**
- Creates timestamped backup of existing file
- Uploads new file (same name, replaces old)
- Verifies upload
- Lists recent backups

## Server Details

- **Server:** 45.56.106.79
- **User:** root
- **RDF Directory:** /var/lib/repec/rdf/
- **Archive Directory:** /var/lib/repec/rdf/archive/

## Deployment Workflow

1. **Generate:** Create RDF from PubPub API
2. **Extract:** Pull out recent records (current quarter)
3. **Enrich:** Add real abstracts from PubPub pages
4. **Clean:** Fix Unicode, add placeholders
5. **Deploy:** Upload to server with backup
6. **Verify:** Check file on server
7. **Wait:** RePEc crawls (1-2 weeks)
8. **Check:** Verify on IDEAS: https://ideas.repec.org/s/bjn/evalua.html
9. **Wait:** Google Scholar indexes (2-4 weeks)
10. **Confirm:** Search Google Scholar

## Quality Checklist

Before deploying, verify:

- [ ] File is pure ASCII (use `file` command)
- [ ] All records have abstracts (real or placeholder)
- [ ] No paper abstracts (only evaluation/response abstracts)
- [ ] Author responses have correct placeholder format
- [ ] Record numbers are sequential and correct
- [ ] File naming follows quarterly convention
- [ ] All required fields present (Title, Author-Name, DOI, etc.)

## Troubleshooting

### Unicode Issues
```bash
# Check for non-ASCII characters
grep --color='auto' -P -n "[^\x00-\x7F]" file.rdf

# Clean with script
venv/bin/python scripts/clean_repec_rdf.py file.rdf file_clean.rdf
```

### Missing Abstracts
```bash
# Find empty abstracts
grep -n "^Abstract: $\|^Abstract:$" file.rdf

# Re-run cleaning to add placeholders
venv/bin/python scripts/clean_repec_rdf.py file.rdf file_fixed.rdf
```

### Deployment Issues
```bash
# Check SSH access
ssh root@45.56.106.79 "ls -lh /var/lib/repec/rdf/"

# Manual upload if script fails
scp file.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

## Google Scholar Citation Linking

For evaluations to appear as citations:

1. **Evaluations must cite the paper** - Add to "References" section on PubPub
2. **Full text must be crawlable** - PubPub pages are public
3. **Wait for indexing** - Can take 4-8 weeks total

Google Scholar detects citations by parsing the full text, not from RePEc metadata.

## Archive Organization

```
repec_rdfs/
├── eval_07_2023.rdf          # Production files
├── eval2024_01.rdf
├── eval2024_02.rdf
├── eval2024_03.rdf
├── eval2025_01.rdf
├── eval2025_02.rdf
├── eval2025_03.rdf
├── eval2025_04.rdf            # Latest production file
└── archive/
    ├── evalX_*.rdf            # Full exports
    └── 2025_04_versions/      # Intermediate files for eval2025_04
        ├── eval2025_04_complete.rdf
        ├── eval2025_04_enriched.rdf
        ├── eval2025_04_test.rdf
        └── eval2025_04_enriched_test.rdf
```

## Related Documentation

- **ABSTRACT_EXTRACTION_STATUS.md** - Latest extraction status
- **docs/archive/** - Historical documentation
- **pypubpub/repec/__init__.py** - RePEcPopulator class
- **scripts/generate_and_deploy_repec.py** - Automated generation script

## Support

For issues:
1. Check troubleshooting section above
2. Review script output for errors
3. Verify file format with `file` command
4. Check server backups if needed
