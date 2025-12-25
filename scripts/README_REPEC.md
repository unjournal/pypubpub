# RePEc Scripts - Quick Reference

## Three-Step Process

### Step 1: Enrich Abstracts
```bash
venv/bin/python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_XX.rdf --output repec_rdfs/eval2025_XX_temp.rdf
```

### Step 2: Clean & Add Placeholders
```bash
venv/bin/python scripts/clean_repec_rdf.py repec_rdfs/eval2025_XX_temp.rdf repec_rdfs/eval2025_XX.rdf
```

### Step 3: Deploy
```bash
./scripts/deploy_repec_rdf.sh repec_rdfs/eval2025_XX.rdf
```

## Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `enrich_repec_abstracts.py` | Extract abstracts from PubPub | RDF file | RDF with real abstracts |
| `clean_repec_rdf.py` | Fix Unicode, add placeholders | RDF file | Pure ASCII RDF |
| `deploy_repec_rdf.sh` | Deploy to server with backup | RDF file | Deployed + backup |

## Quarterly File Names

- Q1: `eval2025_01.rdf` (Jan-Mar)
- Q2: `eval2025_02.rdf` (Apr-Jun)
- Q3: `eval2025_03.rdf` (Jul-Sep)
- Q4: `eval2025_04.rdf` (Oct-Dec)

## Placeholder Formats

**Evaluations:**
```
This is an evaluation of the paper "TITLE" for The Unjournal. Please see the discussion below.
```

**Author Responses:**
```
This is an author response to the Unjournal's evaluation(s) of the paper "TITLE". Please see the discussion below.
```

## Verification Commands

```bash
# Check encoding (should say "ASCII text")
file repec_rdfs/eval2025_04.rdf

# Count records
grep -c "^Template-Type:" repec_rdfs/eval2025_04.rdf

# Check for Unicode issues
grep --color='auto' -P -n "[^\x00-\x7F]" repec_rdfs/eval2025_04.rdf

# View abstracts
grep "^Abstract:" repec_rdfs/eval2025_04.rdf | less
```

## Server Locations

- **Production:** `/var/lib/repec/rdf/eval2025_XX.rdf`
- **Archive:** `/var/lib/repec/rdf/archive/`
- **Server:** `root@45.56.106.79`

## Full Documentation

See `docs/REPEC_DEPLOYMENT.md` for complete guide.
