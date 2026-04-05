# Adding an Evaluation to an Existing PubPub Package

This guide explains how to add a new evaluation to an existing evaluation package on PubPub using the Python automation tools.

> **Alternative: Form-Based Publishing.** New evaluations submitted via the [interactive evaluation form](https://daaronr.github.io/unjournal_tools_interfaces/evaluation_form/) can be published to PubPub directly through the submission API's editorial approval workflow — no manual script needed. See `unjournal_tools_interfaces/evaluation_form/api/DEPLOYMENT.md` for that pipeline. This guide covers the manual/script-based approach for evaluations collected via Coda or other means.

## Prerequisites

1. **PubPub credentials** - Email and password for unjournal.pubpub.org
2. **Python environment** with pypubpub installed
3. **Evaluation data** from the Coda form, the interactive evaluation form export, or PDF

## Quick Start

```bash
# Set password (required)
export PASSWORD="your_pubpub_password"

# Run the script
cd /Users/yosemite/githubs/pypubpub
python scripts/add_evaluation_to_package.py
```

## Step-by-Step Process

### Step 1: Gather Evaluation Data

From the Coda evaluation form, collect:
- Evaluator name (if they consented to public identification)
- Summary text
- All ratings with 90% confidence intervals
- Claims assessment responses
- The full evaluation text/document

**Ratings to collect:**
| Field | Description |
|-------|-------------|
| overall_assessment | Overall assessment (0-100) |
| claims_evidence | Claims, strength, characterization of evidence |
| methods | Methods: Justification, reasonableness, validity, robustness |
| advancing_knowledge | Advancing knowledge and practice |
| logic_communication | Logic & communication |
| open_collaborative | Open, collaborative, replicable |
| real_world_relevance | Real-world relevance |
| relevance_to_global_priorities | Relevance to global priorities |
| journal_tier_normative | Journal tier should (0-5) |
| journal_tier_predictive | Journal tier will (0-5) |

Each rating should have: `lower`, `mid`, `upper` values for the 90% CI.

### Step 2: Identify Target Package

Find the existing evaluation summary:
1. Go to https://unjournal.pubpub.org
2. Find the evaluation summary for the paper
3. Note the **slug** from the URL (e.g., `evalsumgivewelldiscount`)

### Step 3: Create/Modify the Script

Edit `scripts/add_evaluation_to_package.py`:

```python
# Update EVALUATION_DATA with the new evaluator's information
EVALUATION_DATA = {
    'evaluator_name': 'Evaluator Name',
    'is_public': True,  # or False if anonymous
    'paper_title': 'Paper Title',
    'summary': """Summary text from the form...""",
    'ratings': {
        'overall_assessment': {'lower': 24, 'mid': 52, 'upper': 68},
        # ... other ratings
    },
    'main_claim': "...",
    'belief_in_claim': "...",
    'robustness_check': "...",
}

# Update the full evaluation text
EVALUATION_TEXT = """
# Full evaluation content...
"""

# Update the target package
EXISTING_PACKAGE = {
    'summary_slug': 'evalsumgivewelldiscount',  # Change this
}
```

### Step 4: Run the Script

```bash
export PASSWORD="your_password"
python scripts/add_evaluation_to_package.py
```

The script will:
1. Log in to PubPub
2. Find the existing evaluation summary
3. Create a new evaluation pub
4. Import the evaluation content
5. Connect the new pub to the summary
6. Print next steps for manual completion

### Step 5: Manual Follow-up

After running the script, you need to manually:

1. **Review the new pub** - Check formatting at the URL printed
2. **Add author attribution** - In PubPub, add the evaluator as author
3. **Update the evaluation summary** to include:
   - Link to new evaluation in "Evaluations" section
   - New evaluator's ratings in comparison tables
   - Summary in "Evaluation Summaries" section
4. **Update ratings databases** - Add ratings to Coda/data system

## Alternative: Using the API Directly

For more control, use the PubPub API directly:

```python
from pypubpub import Pubshelper_v6
from pypubpub.utils import generate_slug

# Initialize
pubhelper = Pubshelper_v6(
    community_url="https://unjournal.pubpub.org",
    community_id="d28e8e57-7f59-486b-9395-b548158a27d6",
    email="your_email",
    password="your_password"
)
pubhelper.login()

# Create evaluation pub
new_pub = pubhelper.create_pub(
    slug=generate_slug("eval-paper-name-evaluator"),
    title="Evaluation of 'Paper' by Evaluator",
    description="Brief description"
)

# Import content (HTML or Word doc)
file_url = pubhelper.upload_file("/path/to/evaluation.html")
pubhelper.import_to_pub(new_pub['id'], file_url, 'evaluation.html', file_size)

# Connect to summary
pubhelper.connect_pub(
    srcPubId=new_pub['id'],
    targetPubId=summary_pub_id,
    relationType="supplement",
    pubIsParent=False
)

pubhelper.logout()
```

## Ratings Database Integration

**Important:** The pypubpub library handles PubPub API interactions only. It does NOT automatically update:
- Coda databases
- The Unjournal data presentation system
- Any external ratings databases

You must manually:
1. Add ratings to the appropriate Coda table
2. The data presentation at https://unjournal.github.io/unjournaldata/ pulls from these sources

## Troubleshooting

### Common Issues

**Login failed**
- Check your password is correct
- Ensure you're using the hashed password (the library handles hashing)

**Pub not found**
- Verify the slug is correct
- Check if the pub is published vs draft

**Content import failed**
- Check HTML is valid
- Try uploading a Word document instead

**Connection failed**
- Verify both pub IDs exist
- Check you have permission to edit

### Getting Help

- PubPub API docs: https://www.pubpub.org/apiDocs
- pypubpub repo: https://github.com/unjournal/pypubpub
- PubPub ID lookup: https://pubpub.tefkah.com/

## Complete Workflow Checklist

- [ ] Get evaluation data from Coda form
- [ ] Get/convert full evaluation text to markdown/HTML
- [ ] Identify target package slug
- [ ] Update script with evaluation data
- [ ] Run script to create pub and connect
- [ ] Verify new pub content in browser
- [ ] Add evaluator as author in PubPub
- [ ] Update evaluation summary with:
  - [ ] Link to new evaluation
  - [ ] Ratings in comparison tables
  - [ ] Summary text
- [ ] Add ratings to Coda database
- [ ] Verify data presentation updates
