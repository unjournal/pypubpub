# Guide: Fixing Trailing Backslashes Systematically

This guide will help you fix all 246 trailing backslash issues affecting 103 publications.

## Step 1: Set Up Credentials

You need to configure your Unjournal PubPub credentials.

### Option A: Create conf_settings.py

Edit `tests/conf_settings.py` with your Unjournal credentials:

```python
import os

# Unjournal settings
community_url = "https://unjournal.pubpub.org"
community_id = "d28e8e57-7f59-486b-9395-b548158a27d6"
email = "your-email@example.com"  # Your Unjournal admin email
password = "your-password"  # Your password

# Or use environment variables (recommended for security):
# email = os.environ.get("UNJOURNAL_EMAIL")
# password = os.environ.get("UNJOURNAL_PASSWORD")
```

### Option B: Use Environment Variables (More Secure)

```bash
export UNJOURNAL_EMAIL="your-email@example.com"
export UNJOURNAL_PASSWORD="your-password"
```

Then update `tests/conf_settings.py`:

```python
import os

community_url = "https://unjournal.pubpub.org"
community_id = "d28e8e57-7f59-486b-9395-b548158a27d6"
email = os.environ.get("UNJOURNAL_EMAIL")
password = os.environ.get("UNJOURNAL_PASSWORD")
```

## Step 2: Test on One Publication First (DRY RUN)

Before fixing all 103 pubs, test on a single publication:

```bash
# Test on one specific pub (dry run - no changes made)
python fix_backslash_urls.py --pub-slug e2fundraisingcharitablegivingreiley
```

This will:
- Show you what would be changed
- Not make any actual changes
- Help verify the script works correctly

Example output:
```
[DRY RUN] Would fix 10 URLs
  ❌ https://doi.org/10.2139/ssrn.2683621\
  ✅ https://doi.org/10.2139/ssrn.2683621
```

## Step 3: Fix a Single Publication (FOR REAL)

Once you've verified the dry run looks correct:

```bash
# Actually fix one pub
python fix_backslash_urls.py --pub-slug e2fundraisingcharitablegivingreiley --execute
```

It will ask for confirmation before making changes.

## Step 4: Test on a Few Publications

Fix a small batch to ensure everything works:

```bash
# Fix the first 5 pubs
python fix_backslash_urls.py --limit 5 --execute
```

## Step 5: Fix All Affected Publications

Once you're confident it's working:

```bash
# Fix all 103 pubs with trailing backslash issues
python fix_backslash_urls.py --execute
```

This will:
- Process all 103 affected publications
- Fix 246 broken URLs total
- Save a detailed log of all changes
- Take about 2-3 minutes (to avoid rate limiting)

## What the Script Does

For each affected publication:

1. **Fetches** the current pub content from PubPub API
2. **Identifies** all URLs with trailing backslashes
3. **Removes** the trailing backslashes
4. **Updates** the pub via PubPub API
5. **Logs** all changes made

## Safety Features

✅ **Dry run by default** - Won't make changes unless you use `--execute`
✅ **Confirmation prompt** - Asks "Are you sure?" before executing
✅ **Detailed logging** - Saves all changes to a timestamped JSON file
✅ **Rate limiting** - Waits between requests to avoid overload
✅ **Error handling** - Continues even if one pub fails

## Command Reference

```bash
# Show what would be fixed (dry run - default)
python fix_backslash_urls.py

# Actually fix all pubs
python fix_backslash_urls.py --execute

# Fix only one specific pub
python fix_backslash_urls.py --pub-slug SLUG_NAME --execute

# Fix first N pubs (for testing)
python fix_backslash_urls.py --limit 5 --execute

# Get help
python fix_backslash_urls.py --help
```

## Monitoring Progress

The script shows progress in real-time:

```
[1/103] Does online fundraising increase charitable giving?
  Slug: e2fundraisingcharitablegivingreiley
  Expected issues: 10
  Fetching pub text for e2fundraisingcharitablegivingreiley...
  Found 10 URLs to fix
  Updating pub...
  ✓ Successfully fixed 10 URLs

[2/103] The wellbeing cost effectiveness of StrongMinds
  Slug: evalsumstrongminds
  Expected issues: 2
  ...
```

## Results

After completion, you'll get:

1. **Console summary** showing success/error counts
2. **JSON log file** with detailed results: `fix_results_YYYYMMDD_HHMMSS.json`

Example summary:
```
SUMMARY
================================================================================
Total pubs processed: 103
Successful: 103
Errors: 0

✓ Changes have been applied to PubPub

📝 Detailed results saved to fix_results_20251107_183045.json
```

## Troubleshooting

### "Error: Configuration not found"
- Make sure `tests/conf_settings.py` exists with your credentials
- Check that the file has the correct format (see Step 1)

### "Login failed"
- Verify your email and password are correct
- Make sure your account has edit permissions on Unjournal

### "Failed to fetch pub text"
- The pub might not exist or might be private
- Check the pub slug is correct

### Rate limiting errors
- The script includes delays, but if you hit limits, try:
  - `--limit 10` to process in smaller batches
  - Wait a few minutes between batches

## Verification

After running the script:

1. **Spot check** a few fixed publications manually
2. **Re-run the scan** to verify issues are resolved:
   ```bash
   python quick_scan_chatgpt.py
   ```
3. **Check the JSON logs** for the complete list of changes

## Rollback

If something goes wrong:

1. PubPub keeps version history
2. You can manually revert changes through the PubPub web interface
3. The JSON log files have the exact changes made

## Questions?

- Check the detailed log file: `fix_results_*.json`
- Review the script: `fix_backslash_urls.py`
- Re-run scan to verify: `python quick_scan_chatgpt.py`
