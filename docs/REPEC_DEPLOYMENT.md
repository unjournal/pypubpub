# RePEc Deployment Guide for The Unjournal

This guide explains how to generate and deploy RePEc RDF metadata files from unjournal.pubpub.org to your Linode server for RePEc and Google Scholar indexing.

## Quick Start

```bash
# Generate fresh RDF files and deploy to Linode
python scripts/generate_and_deploy_repec.py

# Generate only (no deployment)
python scripts/generate_and_deploy_repec.py --skip-deploy

# Dry run (see what would happen)
python scripts/generate_and_deploy_repec.py --dry-run
```

## What This Does

1. **Connects to unjournal.pubpub.org** - Fetches all published evaluation pubs
2. **Generates RDF files** - Creates RePEc ReDIF-Paper metadata for each pub
3. **Deploys to Linode** - Uploads via SCP to your RePEc archive directory
4. **Triggers indexing** - Notifies RePEc to re-crawl (if automated)

## Prerequisites

### 1. PubPub Credentials (Optional for Public Pubs)

Create `tests/conf_settings.py` (copy from template):

```python
community_url = "https://unjournal.pubpub.org"
community_id = "d28e8e57-7f59-486b-9395-b548158a27d6"
email = "your@email.com"  # Optional for public pubs
password = "your_password"  # Optional for public pubs
```

Or set environment variables:
```bash
export PUBPUB_COMMUNITY_URL="https://unjournal.pubpub.org"
export PUBPUB_COMMUNITY_ID="d28e8e57-7f59-486b-9395-b548158a27d6"
export PUBPUB_EMAIL="your@email.com"
export PUBPUB_PASSWORD="your_password"
```

### 2. SSH Access to Linode Server

You need SSH access to your Linode server (45.56.106.79):

```bash
# Test connection
ssh root@45.56.106.79

# Set up SSH key if you haven't already (recommended)
ssh-copy-id root@45.56.106.79
```

### 3. RePEc Archive Directory Structure

On your Linode server, you need a proper RePEc archive structure:

```
/var/lib/repec/
└── rdf/
    ├── bjnecon.rdf           # Archive metadata
    ├── bjnevalua.rdf          # Series metadata
    ├── unjournal_eval_YYYYMMDD.rdf  # Evaluation records
    └── latest.rdf -> unjournal_eval_YYYYMMDD.rdf
```

## Server Setup

### Initial Setup on Linode

SSH into your server and create the directory structure:

```bash
ssh root@45.56.106.79

# Create RePEc directory
mkdir -p /var/lib/repec/rdf
cd /var/lib/repec/rdf

# Create archive metadata (bjnecon.rdf)
cat > bjnecon.rdf << 'EOF'
Template-Type: ReDIF-Archive 1.0
Handle: RePEc:bjn
Name: The Unjournal Evaluations
Maintainer-Email: contact@unjournal.org
Description: Open evaluations of research papers by The Unjournal
URL: https://unjournal.pubpub.org/
Maintainer-Name: The Unjournal
EOF

# Create series metadata (bjnevalua.rdf)
cat > bjnevalua.rdf << 'EOF'
Template-Type: ReDIF-Series 1.0
Name: The Unjournal Evaluation Papers
Provider-Name: The Unjournal
Provider-Homepage: https://unjournal.org
Provider-Institution: RePEc:edi:bjnecon
Maintainer-Email: contact@unjournal.org
Type: ReDIF-Paper
Handle: RePEc:bjn:evalua
Description: Research evaluations and evaluation summaries published by The Unjournal
Classification-JEL: A14
EOF

# Set permissions
chmod 644 *.rdf
```

### Optional: Create Auto-Update Script

Create a script on the server to notify RePEc of updates:

```bash
# Create update script
cat > /usr/local/bin/repec-update.sh << 'EOF'
#!/bin/bash
# Update RePEc last-modified timestamp
touch /var/lib/repec/rdf/latest.rdf
echo "RePEc files updated at $(date)"
# Add any additional notification steps here
EOF

chmod +x /usr/local/bin/repec-update.sh
```

## Usage Examples

### Generate Fresh RDF and Deploy

```bash
# Standard usage - generates and deploys
python scripts/generate_and_deploy_repec.py

# Output:
# 📚 Fetching pubs from https://unjournal.pubpub.org...
# 📝 Generating RePEc RDF metadata...
# ✅ Generated 87 records
# 📄 RDF file: repec_rdfs/evalX_123456.rdf
# 🚀 Deploying to Linode server 45.56.106.79...
# ✅ Successfully uploaded
# ✅ Complete!
```

### Generate Only (Test First)

```bash
# Generate without deploying (useful for testing)
python scripts/generate_and_deploy_repec.py --skip-deploy
```

### Dry Run (See What Would Happen)

```bash
# Preview without making changes
python scripts/generate_and_deploy_repec.py --dry-run
```

### Custom Server Settings

```bash
# Use different server/paths
python scripts/generate_and_deploy_repec.py \
  --server my.server.com \
  --user repec \
  --remote-path /home/repec/archive/
```

## RDF File Format

The generated RDF files use the ReDIF-Paper 1.0 template format:

```
Template-Type: ReDIF-Paper 1.0
Author-Name: Jane Doe
Author-Name: John Smith
Title: Evaluation Summary and Metrics: "Paper Title"
Abstract: Evaluation Summary and Metrics of "Paper Title" for The Unjournal.
DOI: https://doi.org/10.21428/d28e8e57.abc123
Publication-Status: Published in The Unjournal
File-URL: https://unjournal.pubpub.org/pub/evalsum-paper-slug
File-Format: text/html
Creation-Date: 2025-08-31
Handle: RePEc:bjn:evalua:evalsum-paper-slug
Number: 2025-42
```

## How RePEc Indexing Works

1. **You upload RDF files** to your server's RePEc archive directory
2. **RePEc crawlers** periodically scan registered archives (usually daily)
3. **RePEc processes** the RDF files and indexes the records
4. **Records appear** on RePEc IDEAS: https://ideas.repec.org/s/bjn/evalua.html
5. **Google Scholar** picks up records from RePEc (usually within days)

### Timeline

- **Upload**: Immediate
- **RePEc indexing**: 1-24 hours (next crawler run)
- **IDEAS display**: After indexing completes
- **Google Scholar**: 1-7 days after RePEc indexes

## Registering Your Archive with RePEc

If this is your first time, you need to register your archive:

1. Visit: https://authors.repec.org/
2. Create account and register your archive
3. Provide archive details:
   - **Handle**: RePEc:bjn
   - **Name**: The Unjournal Evaluations
   - **URL**: http://45.56.106.79/repec/ (or your domain)
   - **Maintainer**: Your contact info

4. RePEc will start crawling your archive automatically

## Verification

### Check Files on Server

```bash
# List RDF files
ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/"

# View latest file
ssh root@45.56.106.79 "cat /var/lib/repec/rdf/latest.rdf | head -30"
```

### Check RePEc Indexing

After upload, verify your records appear on RePEc:

- **Archive**: https://ideas.repec.org/s/bjn/evalua.html
- **Individual records**: https://ideas.repec.org/p/bjn/evalua/your-slug.html

### Check Google Scholar

Search for your paper titles or DOIs in Google Scholar:
- https://scholar.google.com/

Records should appear with citation "Published in The Unjournal" and link to PubPub.

## Troubleshooting

### Permission Denied on SCP

```bash
# Add your SSH key to the server
ssh-copy-id root@45.56.106.79

# Or check server permissions
ssh root@45.56.106.79 "ls -ld /var/lib/repec/rdf/"
```

### RePEc Not Crawling

1. **Verify archive registration**: Check https://authors.repec.org/
2. **Check file accessibility**: Make sure RDF files are publicly accessible
3. **Manual notification**: Contact RePEc support to trigger a crawl
4. **Check logs**: If you have web server logs, check for RePEc crawler

### Google Scholar Not Indexing

1. **Wait longer**: Can take up to 7 days
2. **Verify RePEc**: Must be on RePEc first
3. **Check DOIs**: Make sure DOIs are valid and registered
4. **Check robots.txt**: Ensure your server allows crawlers

### Missing Pubs in RDF

The RDF generator filters out:
- Template pubs (slug contains "template")
- Admin pubs (author: "Unjournal Admin")
- Unpublished pubs (unless you provide credentials)

To include unpublished pubs, provide login credentials in `conf_settings.py`.

## Automated Updates

### Cron Job (Recommended)

Set up a weekly cron job to automatically update RePEc:

```bash
# On your local machine or CI server
crontab -e

# Add this line (runs every Sunday at 2am)
0 2 * * 0 cd /path/to/pypubpub && python scripts/generate_and_deploy_repec.py
```

### GitHub Actions (Alternative)

Create `.github/workflows/repec-update.yml`:

```yaml
name: Update RePEc
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2am UTC
  workflow_dispatch:  # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -e .
      - name: Generate and deploy
        env:
          PUBPUB_COMMUNITY_URL: ${{ secrets.PUBPUB_COMMUNITY_URL }}
          PUBPUB_COMMUNITY_ID: ${{ secrets.PUBPUB_COMMUNITY_ID }}
        run: python scripts/generate_and_deploy_repec.py
```

## Related Resources

- **RePEc Registration**: https://authors.repec.org/
- **ReDIF Format Spec**: https://ideas.repec.org/t/rdf.html
- **RePEc IDEAS**: https://ideas.repec.org/
- **Google Scholar**: https://scholar.google.com/
- **The Unjournal**: https://unjournal.org/

## Questions?

- Check server logs: `ssh root@45.56.106.79 "tail /var/log/syslog"`
- Test SCP manually: `scp test.txt root@45.56.106.79:/var/lib/repec/rdf/`
- Contact RePEc support: https://ideas.repec.org/gettsup.html
