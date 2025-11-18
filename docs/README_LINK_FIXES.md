# Link Issues and Systematic Fixes

This directory contains tools to identify and fix link issues on unjournal.pubpub.org.

## What Was Found

Scanned **189 published publications** and discovered:

### 🔴 Critical: Trailing Backslashes
- **246 broken URLs** with trailing `\` characters
- Affects **103 publications** (54% of all content!)
- These URLs return 404 errors
- **Can be fixed automatically** ✅

### 🟡 Important: Inaccessible ChatGPT Links
- **11 ChatGPT conversation links** found
- **10 are inaccessible** (404/403 errors)
- **1 is accessible** ✅
- Requires manual intervention (contact authors)

## Files Created

### Documentation
- **QUICKSTART_FIX_BACKSLASHES.md** - 5-minute quick start guide
- **FIXING_BACKSLASHES_GUIDE.md** - Detailed fixing guide
- **LINK_ISSUES_REPORT.md** - Complete analysis report

### Scripts
- **setup_credentials.py** - Interactive credentials setup
- **test_credentials.py** - Test your PubPub connection
- **fix_backslash_urls.py** - Main fix script (automated)
- **scan_links.py** - Full link scanner
- **quick_scan_chatgpt.py** - Fast scan for issues
- **test_chatgpt_links.py** - Test ChatGPT link accessibility

### Results Data
- **quick_scan_results.json** - All issues found
- **chatgpt_accessibility_results.json** - ChatGPT link test results

## Quick Start: Fix the Backslashes

### 1️⃣ Setup (1 minute)
```bash
python setup_credentials.py
```

### 2️⃣ Test (1 minute)
```bash
python test_credentials.py
```

### 3️⃣ Preview (1 minute)
```bash
python fix_backslash_urls.py --pub-slug e2fundraisingcharitablegivingreiley
```

### 4️⃣ Fix All (3 minutes)
```bash
python fix_backslash_urls.py --execute
```

**Total time: ~5 minutes to fix all 246 issues across 103 publications**

## The Automated Fix

The script will:

1. Login to PubPub with your credentials
2. For each of the 103 affected publications:
   - Fetch the content
   - Find URLs ending with `\`
   - Remove the trailing backslashes
   - Update the publication
   - Log all changes
3. Generate a detailed report

### Example Fix

```
Before: https://doi.org/10.2139/ssrn.2683621\  ❌ 404 Error
After:  https://doi.org/10.2139/ssrn.2683621   ✅ Works!
```

## Manual Fixes Required

### ChatGPT Links

The following publications have inaccessible ChatGPT links that need manual attention:

**"Irrigation Strengthens Climate Resilience"** (6 dead links)
- Edit: https://unjournal.pubpub.org/pub/evalsumirrigationresilience/draft
- Action: Contact evaluator to re-share conversations or provide alternatives

**"Adaptability and the Pivot Penalty"** (4 dead links)
- Edit: https://unjournal.pubpub.org/pub/evalsumpivotpenalty/draft
- Edit: https://unjournal.pubpub.org/pub/e1pivotpenalty/draft
- Action: Contact evaluator to re-share conversations or provide alternatives

See `LINK_ISSUES_REPORT.md` for complete details and all URLs.

## Safety Features

✅ **Dry run by default** - Preview changes before applying
✅ **Confirmation prompts** - Asks before making changes
✅ **Detailed logging** - Records every change made
✅ **Rate limiting** - Respectful to PubPub servers
✅ **Error handling** - Continues even if one pub fails
✅ **Version history** - PubPub keeps previous versions

## Command Cheat Sheet

```bash
# Setup
python setup_credentials.py          # Configure credentials
python test_credentials.py           # Test connection

# Scanning
python quick_scan_chatgpt.py         # Fast scan for issues
python test_chatgpt_links.py         # Test ChatGPT links
python scan_links.py                 # Full deep scan (slow)

# Fixing (Preview)
python fix_backslash_urls.py         # Preview all fixes
python fix_backslash_urls.py --pub-slug SLUG  # Preview one pub
python fix_backslash_urls.py --limit 5        # Preview first 5

# Fixing (Execute)
python fix_backslash_urls.py --execute       # Fix all pubs
python fix_backslash_urls.py --pub-slug SLUG --execute  # Fix one
python fix_backslash_urls.py --limit 5 --execute        # Fix first 5

# Help
python fix_backslash_urls.py --help  # Show all options
```

## Workflow Recommendation

1. **Read QUICKSTART_FIX_BACKSLASHES.md** first
2. **Run the automated fix** for trailing backslashes (5 minutes)
3. **Verify** the fixes worked with `quick_scan_chatgpt.py`
4. **Manually address** the 10 inaccessible ChatGPT links
5. **Re-scan** periodically to catch new issues

## Questions?

- **Quick start**: `QUICKSTART_FIX_BACKSLASHES.md`
- **Detailed guide**: `FIXING_BACKSLASHES_GUIDE.md`
- **Full analysis**: `LINK_ISSUES_REPORT.md`
- **Results data**: `quick_scan_results.json`

## Prevention

To prevent future trailing backslash issues:

1. Review the content import/export process
2. Check if there's a bug in the PubPub editor
3. Train editors to avoid copying/pasting with extra characters
4. Consider periodic automated scans

---

**Ready to fix 246 broken links in 5 minutes?**

Start here: `python setup_credentials.py`
