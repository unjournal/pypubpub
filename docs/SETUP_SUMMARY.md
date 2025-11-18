# Setup Summary: Automating Unjournal Evaluation Packages

## ✅ What's Been Completed

### 1. Production Folder Status
- **Verified:** The `unjournalpubpub_production_moved` folder is NOT git-tracked
- **Credentials found:** In `unjournalpubpub_production_moved/conf.py`
  - Community: https://unjournal.pubpub.org
  - Community ID: d28e8e57-7f59-486b-9395-b548158a27d6

### 2. Paper & Evaluations Identified

**Paper:**
- Title: "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
- Authors: Daniel J. Benjamin, Kristen Cooper, Ori Heffetz, Miles S. Kimball, Jiannan Zhou
- DOI: **10.3386/w31728** (NBER Working Paper)
- SSRN: 10.2139/ssrn.4568587

**Evaluators:**

1. **Caspar Kaiser** (Pseudonym: Friedrich)
   - Wants to be publicly identified: YES
   - Review file: `/tmp/review_data/main.tex` (LaTeX format)
   - Summary: "This is a major methodological innovation in how we can adjust for differences in scale-use. The empirical component would especially benefit from more diverse and reliable samples."
   - All ratings extracted ✓

2. **Alberto Prati** (Pseudonym: Prati)
   - Form data available
   - Overall rating: 95 (90-100)
   - **⚠️ ACTION NEEDED:** Need to extract complete ratings from full PDF form
   - **⚠️ ACTION NEEDED:** Need to locate or request written evaluation text

### 3. Files Created

#### `create_eval_scale_use.py`
- Main automation script to create evaluation package
- Contains all Caspar's ratings
- Has placeholders for Prati's complete data
- Ready to run once dependencies are installed

####  `AUTOMATION_GUIDE.md`
- Complete documentation of the automation process
- Workflow for draft vs final packages
- Data structure specifications
- Templates for evaluation summaries and individual evaluations
- Technical notes and next steps

#### `SETUP_SUMMARY.md`
- This file - quick reference guide

### 4. Evaluation Data Extracted

**Caspar Kaiser - Complete Ratings:**

| Criterion | Lower CI | Midpoint | Upper CI |
|-----------|----------|----------|----------|
| Overall assessment | 80 | 95 | 100 |
| Claims, evidence | 70 | 80 | 90 |
| Methods | 80 | 90 | 100 |
| Advancing knowledge | 80 | 90 | 100 |
| Logic & communication | 60 | 75 | 90 |
| Open, replicable | 70 | 85 | 90 |
| Journal tier (merit) | 4.7 | 4.1 | 5.0 |
| Journal tier (prediction) | 4.4 | 4.0 | 5.0 |

**Key Comments:**
- Overall: "I know few papers in this specific field from the last few years that are more important than this."
- Logic & Communication: "The reasoning itself was sound and very thorough. As noted in my review, the paper itself could have been more accessible."
- Relevance to global priorities: Left open - noted this is fundamental science, will eventually be relevant to practitioners

**Evaluation Details:**
- Field: Methods for subjective wellbeing research
- Years in field: Since about 2018
- Reviews completed: 10+
- Time spent on this evaluation: ~8 hours

## 📋 Next Steps

### Immediate Actions Needed

1. **Extract Prati's complete ratings**
   - Source: `/Users/yosemite/Downloads/prati_The Unjournal Hub (internal) · Eval. Form, acad. stream, revamped.pdf`
   - Need all 7 percentile ratings + 2 journal tiers
   - Need all comments on ratings

2. **Locate or request Prati's written evaluation**
   - Check if there's a separate document we haven't found
   - If not, request from Prati or evaluation manager

3. **Convert Caspar's LaTeX review to markdown**
   - Source: `/tmp/review_data/main.tex`
   - Target: Markdown or HTML for PubPub import
   - Preserve citations and formatting

### To Run the Automation

```bash
# Navigate to project directory
cd /Users/yosemite/githubs/pypubpub

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
pip install requests

# Run the evaluation creation script
python create_eval_scale_use.py
```

The script will:
1. Display all ratings in table format
2. Ask for confirmation before creating package structure
3. Create the evaluation package on PubPub (when you choose 'yes')

### After Package Creation

1. **Draft Phase** (Share with authors - keep anonymous):
   - Import evaluations into PubPub
   - Add ratings tables
   - Link all pubs together
   - Share with paper authors for response

2. **Final Phase** (After author response):
   - Add author response if provided
   - Add evaluator names (Caspar & Prati both want to be identified)
   - Publish all pubs
   - Request DOIs

## 📁 File Locations

- **Caspar's review:** `/tmp/review_data/main.tex`
- **Caspar's form:** `/Users/yosemite/Downloads/caspar_The Unjournal Hub (internal) · Eval. Form, acad. stream, revamped.pdf`
- **Prati's form:** `/Users/yosemite/Downloads/prati_The Unjournal Hub (internal) · Eval. Form, acad. stream, revamped.pdf`
- **Instruction docs:**
  - `/Users/yosemite/Downloads/Unjournal pubpub current process (1).md`
  - `/Users/yosemite/Downloads/Unjournal Pubpub  V6 V7  process and automation.md`
  - `/Users/yosemite/Downloads/TEST BACKUP Copy of The Unjournal Hub (internal) · curating_hosting evals.pdf`

## 🔧 Technical Details

### PubPub Package Structure

```
Evaluation Summary and Metrics
├── Evaluation 1 (Caspar Kaiser / Friedrich)
│   ├── Summary measures (key ratings)
│   ├── Written report (from LaTeX)
│   └── Evaluator details
├── Evaluation 2 (Alberto Prati / Prati)
│   ├── Summary measures
│   ├── Written report (TBD)
│   └── Evaluator details
└── Author Response (to be added later)
```

### Connections
- Each evaluation is a "supplement to" the summary
- Summary "is a review of" the original paper (DOI: 10.3386/w31728)

### DOI Strategy
- Request DOI for Evaluation Summary only
- Individual evaluations and author response are "peer reviews" based on connections

## 🎯 Automation Roadmap

### Phase 1: Current Setup ✅
- [x] Structure creation script
- [x] Data extraction from forms
- [x] Documentation

### Phase 2: Content Processing (In Progress)
- [ ] Extract all Prati ratings
- [ ] LaTeX to Markdown converter
- [ ] Auto-generate ratings tables
- [ ] Template system for summaries

### Phase 3: Full Automation (Future)
- [ ] Direct API pub creation
- [ ] Automatic content import
- [ ] Connection management via API
- [ ] Integration with RePEc generation

## 📞 Questions to Resolve

1. **Prati's evaluation:** Do we have a separate written evaluation document, or just the form ratings?

2. **Evaluation manager:** Who should be listed as the evaluation manager for this package?

3. **Template pubs:** Do template pubs exist on PubPub that we should download/copy from?

4. **Draft sharing:** What's the preferred method for sharing draft packages with authors?

## 🚀 Ready to Proceed

The automation infrastructure is in place! Once you:
1. Complete Prati's data extraction
2. Convert Caspar's LaTeX review
3. Run the script

You'll have a complete draft evaluation package ready to share with the paper authors.

**See `AUTOMATION_GUIDE.md` for detailed workflow and templates.**
