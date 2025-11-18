# Coda to PubPub Workflow

## Overview

This workflow fetches evaluation data from Coda.io and prepares it for posting to PubPub, while keeping sensitive information (pseudonyms, confidential comments) secure and local-only.

## Security Model

### What's Kept Private (gitignored)

1. **`evaluation_data/confidential/`** - Contains:
   - Evaluator real names (when they want to be anonymous)
   - Pseudonyms and hash codes
   - Confidential comments to editors
   - Identity preferences

2. **`.env`** file - Contains:
   - Coda API key
   - PubPub credentials
   - Other secrets

3. **`unjournalpubpub_production_moved/conf.py`** - Contains credentials

### What's Public (safe to commit)

1. **`evaluation_data/public/`** - Contains:
   - Paper metadata
   - Ratings and confidence intervals
   - Public comments on ratings
   - Evaluation summaries
   - Hash IDs (non-reversible identifiers)

2. **Scripts** - Automation code (no secrets)

3. **Documentation** - This file and guides

## Setup

### 1. Install Dependencies

```bash
pip install codaio python-dotenv
```

### 2. Get Coda API Key

1. Go to https://coda.io/account
2. Generate an API key
3. Copy the key

### 3. Find Your Coda IDs

**Document ID:**
- From URL: `https://coda.io/d/_dXXXXXXXXXX`
- The part after `/d/`

**Table ID:**
- Open the table in Coda
- Click "..." → "Copy table link"
- Extract the table ID from the URL

### 4. Create .env File

```bash
cp .env.example .env
# Edit .env and add your actual values
```

**Never commit .env to git!**

## Usage

### Fetch Data for Specific Paper

```bash
python fetch_from_coda.py "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
```

This will:
1. Connect to Coda API
2. Fetch all evaluations for that paper
3. Separate sensitive data
4. Save to:
   - `evaluation_data/public/adjusting_for_scale_use_heterogeneity_evaluations.json`
   - `evaluation_data/confidential/adjusting_for_scale_use_heterogeneity_sensitive.json`

### Fetch All Evaluations

```bash
python fetch_from_coda.py
```

## Data Structure

### Public Data (Safe to Commit)

```json
[
  {
    "hash_id": "a1b2c3d4e5f6g7h8",
    "paper_title": "Paper Title",
    "summary": "Evaluator's public summary",
    "ratings": {
      "overall_assessment": {
        "lower": 80,
        "mid": 95,
        "upper": 100
      }
    },
    "comments": {
      "overall": "Public comments on rating"
    },
    "submission_date": "2024-11-15"
  }
]
```

### Sensitive Data (NEVER Commit)

```json
{
  "a1b2c3d4e5f6g7h8": {
    "hash_id": "a1b2c3d4e5f6g7h8",
    "evaluator_name": "Dr. Jane Smith",
    "pseudonym": "Friedrich",
    "confidential_comments": "Private notes...",
    "wants_public_id": true
  }
}
```

## Integration with PubPub Posting

### Phase 1: Draft Package (Anonymous)

```python
from fetch_from_coda import main
import json

# Fetch data
pubpub_data = main("Paper Title Here")

# Use DRAFT version (anonymous)
for eval in pubpub_data:
    draft_eval = eval["draft"]
    # draft_eval contains pseudonym, no real name
    # Use this for creating package to share with authors
```

### Phase 2: Final Package (After Author Response)

```python
# Use FINAL version (with names if evaluators agreed)
for eval in pubpub_data:
    final_eval = eval["final"]
    # final_eval contains real name if wants_public_id == true
    # Use this for publishing
```

## Coda Form Field Mapping

Based on the evaluation form, these fields are extracted:

### Public Fields
- Paper title
- Evaluation summary
- All ratings (9 criteria × 3 values each)
- Public comments on ratings
- Claim assessment
- Evaluator expertise (if not identifying)

### Sensitive Fields (Gitignored)
- "Would you like to be publicly identified as the author"
- "salted hash code or pseudonym"
- "Confidential comments section"
- Real name (if provided)

## Workflow Diagram

```
Coda Form Submission
       ↓
   Coda Table
       ↓
fetch_from_coda.py (THIS SCRIPT)
       ↓
   ┌───────────────┴──────────────┐
   ↓                              ↓
evaluation_data/public/      evaluation_data/confidential/
(Safe to commit)             (GITIGNORED - local only)
   ↓                              ↓
   └──────────┬───────────────────┘
              ↓
    create_eval_package.py
              ↓
        PubPub Package
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
Draft (Anonymous)   Final (With Names)
    ↓                   ↓
Share w/Authors     Publish
```

## Automated Daily Sync (Optional)

Similar to unjournaldata repo, you can set up GitHub Actions:

```yaml
# .github/workflows/sync-coda.yml
name: Sync from Coda

on:
  schedule:
    - cron: '30 13 * * *'  # Daily at 13:30 UTC
  workflow_dispatch:  # Manual trigger

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install codaio python-dotenv

      - name: Fetch from Coda
        env:
          CODA_API_KEY: ${{ secrets.CODA_API_KEY }}
          CODA_DOC_ID: ${{ secrets.CODA_DOC_ID }}
          CODA_TABLE_ID: ${{ secrets.CODA_TABLE_ID }}
        run: |
          python fetch_from_coda.py

      - name: Commit public data only
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add evaluation_data/public/
          git commit -m "Auto-update public evaluation data" || echo "No changes"
          git push
```

**Note:** Only public data gets committed. Sensitive data stays local.

## FAQ

### Q: What if an evaluator wants to remain anonymous?

A: In the draft phase, we use their pseudonym/hash code. In the final phase, we still use the pseudonym unless they explicitly checked "wants_public_id".

### Q: Can I see the pseudonyms in the code?

A: No! Pseudonyms are stored only in `evaluation_data/confidential/` which is gitignored. Public code only sees hash IDs.

### Q: How do I match evaluations between systems?

A: Use the `hash_id` field. It's generated from evaluator name + paper title + salt, so it's:
- Consistent (same eval always gets same hash)
- Non-reversible (can't get name from hash)
- Unique (different evals get different hashes)

### Q: What about Prati's current data?

For the immediate need, you can manually create a local file:

```bash
# Create the sensitive data file locally
cat > evaluation_data/confidential/scale_use_prati.json << 'EOF'
{
  "evaluator_name": "Alberto Prati",
  "pseudonym": "Prati",
  "wants_public_id": true,
  "confidential_comments": ""
}
EOF
```

Then extract ratings from the PDF and add to `create_eval_scale_use.py`.

## Next Steps

1. ✅ Set up `.env` with Coda credentials
2. ✅ Run `fetch_from_coda.py` to pull data
3. ✅ Review public JSON files (safe to share)
4. ✅ Use data to create PubPub packages
5. ⚠️ Never commit `evaluation_data/confidential/` or `.env`
