# RePEc Scripts - Quick Reference

## Automated refresh (recommended)

One command does the whole routine refresh: pull, generate, clean, validate,
deploy, commit and push.

```bash
./scripts/repec_refresh.sh              # full run
./scripts/repec_refresh.sh --dry-run    # generate + validate only
./scripts/repec_refresh.sh --no-deploy  # skip the Linode upload
```

Paths are resolved relative to the script, so it works from any checkout. It
picks the interpreter from `$REPEC_PYTHON`, then `.venv312/`, `.venv/`,
miniforge, then `python3`.

**It must run on a machine that has the credentials and the deploy SSH key.**
It needs `tests/conf_settings.py` (or `PUBPUB_COMMUNITY_ID` / `PUBPUB_EMAIL` /
`PUBPUB_PASSWORD`), plus network access to `unjournal.pubpub.org` and SSH to the
Linode host. An ephemeral cloud container has none of these, so schedule this
locally (cron/launchd) rather than as a cloud agent task. The script checks for
credentials up front and exits with a clear message instead of a traceback.

Behaviour worth knowing:

- **0 new records** is a success, not a failure — it means everything published
  is already covered. The empty file is removed and nothing is deployed.
- **Validation is a hard gate.** Nothing is deployed or committed if a blocking
  check fails.
- **Rejected files are quarantined** to `repec_rdfs/failed/`. This matters: the
  generator treats every `*.rdf` directly inside `repec_rdfs/` as
  already-published, so a rejected file left in place would permanently suppress
  those records on all future runs.

## Validating a file on its own

```bash
python scripts/validate_repec_rdf.py <file.rdf> [repec_rdfs/]
```

Blocking (exit 1): duplicate handles inside the file, handles already present in
`repec_rdfs/*.rdf`, template/blacklisted entries, records missing
`Template-Type`, `Title`, `Handle`, `Creation-Date` or `File-URL`.

Warnings (exit 0): odd handle or number format, empty/placeholder abstracts,
missing DOI, and overlap with superseded copies under `repec_rdfs/archive/`.

The duplicate check deliberately scans `repec_rdfs/*.rdf` non-recursively, to
match exactly the corpus the generator dedups against. `archive/` holds
superseded working copies of the same records, so blocking on those would
deadlock every run.

## Manual three-step process

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
