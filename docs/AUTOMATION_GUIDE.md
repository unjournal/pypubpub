# Automation Guide: Posting Unjournal Evaluation Packages

## Overview

This guide documents the process of automating the creation and posting of evaluation packages to PubPub for The Unjournal.

## Current Status (November 2025)

### What We Have

1. **Paper being evaluated:** "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
   - DOI: `10.3386/w31728` (NBER Working Paper)
   - Authors: Daniel J. Benjamin, Kristen Cooper, Ori Heffetz, Miles S. Kimball, Jiannan Zhou

2. **Evaluations received:**
   - **Caspar Kaiser** (pseudonym: Friedrich)
     - Full LaTeX review: `/tmp/review_data/main.tex`
     - Complete ratings extracted from PDF form
     - Wants to be publicly identified

   - **Alberto Prati** (pseudonym: Prati)
     - Form data in PDF
     - Need to extract complete ratings
     - Written evaluation text: TBD (may need to request)

### Files Created

- `create_eval_scale_use.py` - Main script to create the evaluation package structure
- `AUTOMATION_GUIDE.md` - This documentation

## Process Workflow

### Phase 1: Draft Package (Share with Authors - ANONYMOUS)

1. **Create package structure** using `EvaluationPackage` class
   - Use DOI to pull paper metadata
   - Create evaluation summary pub
   - Create individual evaluation pubs (empty placeholders)

2. **Populate evaluation summary**
   - Add evaluation manager notes
   - Create ratings table (WITHOUT evaluator names)
   - Add evaluation summaries
   - Link to original paper

3. **Populate individual evaluations**
   - Import evaluation text (from LaTeX/Word/etc)
   - Add ratings for this evaluator
   - Use PSEUDONYMS only

4. **Create connections**
   - Link evaluations as "supplements" to summary
   - Link summary as "review of" original paper

5. **Share with authors** for response (all anonymous at this stage)

### Phase 2: Final Package (After Author Response)

6. **Add author response** if provided

7. **Add evaluator names** (only for those who want to be identified)
   - Update author attribution
   - Add ORCID IDs if available

8. **Publish** all pubs in the package

9. **Request DOIs** for evaluation summary

10. **Update RePEc** metadata

## Data Structure

### Evaluation Package Components

```
Evaluation Summary and Metrics (main pub)
├── Evaluation 1 (Caspar Kaiser)
├── Evaluation 2 (Alberto Prati)
└── Author Response (if provided)
```

### Required Data for Each Evaluator

```python
{
    "name": "Caspar Kaiser",
    "pseudonym": "Friedrich",
    "identified": True,  # Want to be named?
    "summary": "Short summary text",
    "review_file": "path/to/review.tex",
    "ratings": {
        "overall_assessment": {"lower": 80, "mid": 95, "upper": 100},
        "claims_evidence": {...},
        "methods": {...},
        "advancing_knowledge": {...},
        "logic_communication": {...},
        "open_replicable": {...},
        "relevance_global": {...},
        "journal_merit": {"lower": 4.7, "mid": 4.1, "upper": 5.0},
        "journal_prediction": {...}
    },
    "comments": {
        "overall": "Comment on overall rating",
        # ... comments on other criteria
    }
}
```

## Templates

### Evaluation Summary Template Structure

```markdown
# Evaluation Summary and Metrics: "[Title]" for The Unjournal

**Evaluators:** [Anonymous during draft phase]

## Paper Metadata
- **Title:** ...
- **Authors:** ...
- **DOI:** ...

## Evaluations

[Links to individual evaluations]

## Overall Ratings

| Criterion | Eval 1 | Eval 2 | Average |
|-----------|--------|--------|---------|
| Overall   | 95 (80-100) | 95 (90-100) | 95 |
| ... | | | |

## Evaluation Summaries

### Evaluation 1
[Summary text]

### Evaluation 2
[Summary text]

## Metrics

[Full ratings table with confidence intervals]

## Author Response

[Added after author has chance to respond]
```

### Individual Evaluation Template

```markdown
# Evaluation [#] of "[Paper Title]" for The Unjournal

**Evaluator:** [Pseudonym during draft]

## Summary

[Evaluator's summary]

## Summary Measures

| Criterion | Lower CI | Midpoint | Upper CI |
|-----------|----------|----------|----------|
| Overall   | 80 | 95 | 100 |

## Written Report

[Full evaluation text - imported from evaluator's document]

## Evaluator Details

- Field: ...
- Years in field: ...
- Time spent: ...
```

## Automation Tasks

### High Priority
- [ ] Extract complete ratings from Prati's PDF form
- [ ] Convert Caspar's LaTeX review to markdown/HTML for PubPub
- [ ] Create script to auto-generate ratings tables
- [ ] Automate pub creation via API

### Medium Priority
- [ ] Template system for evaluation summaries
- [ ] Automatic DOI metadata fetching
- [ ] Citation formatting automation

### Future
- [ ] Direct integration with evaluation submission forms
- [ ] Automatic email notifications
- [ ] Integration with RePEc generation

## Next Steps for Scale-Use Heterogeneity Paper

1. Extract all Prati ratings from PDF
2. Convert Caspar's LaTeX to suitable format
3. Run `create_eval_scale_use.py` to create structure
4. Manually populate content in PubPub
5. Share draft with paper authors
6. After response, finalize and publish

## Technical Notes

### PubPub API Access
- Email: `contact@unjournal.org`
- Community URL: `https://unjournal.pubpub.org`
- Community ID: `d28e8e57-7f59-486b-9395-b548158a27d6`

### Dependencies
```bash
pip install git+https://github.com/unjournal/pypubpub@main
pip install bibtexparser nltk pycryptodome pyparsing
```

### Key Classes
- `Pubshelper_v6` - Core PubPub API client
- `EvaluationPackage` - High-level evaluation package creator
- `Migratehelper_v6` - Migration and manipulation helper

## References

- [PubPub API Docs](https://www.pubpub.org/apiDocs)
- [Unjournal Process Doc](https://docs.google.com/document/d/1F9w46tN3u8eeE8f5iTi543eDxAf9BTJ1OXJgxDHtPsw/edit)
- [pypubpub CLAUDE.md](/pypubpub/CLAUDE.md)
