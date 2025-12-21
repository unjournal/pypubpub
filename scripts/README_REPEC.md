# RePEc Update Scripts

Scripts for generating and deploying RePEc RDF metadata to Linode server.

## Quick Start

```bash
# Generate and deploy in one command
./scripts/update_repec.sh

# Generate only (no deployment)
./scripts/update_repec.sh --skip-deploy

# Test without making changes
./scripts/update_repec.sh --dry-run
```

## What These Scripts Do

1. **`update_repec.sh`** - Wrapper script that ensures correct Python version
2. **`generate_and_deploy_repec.py`** - Main script that:
   - Fetches all pubs from unjournal.pubpub.org
   - Generates RePEc ReDIF metadata (RDF format)
   - Uploads to Linode server (45.56.106.79)
   - Creates symlink to latest.rdf

## Requirements

- **Python 3.10+** (uses union type syntax)
- **SSH access** to 45.56.106.79
- **PubPub credentials** (optional for public pubs)

## Setup

### 1. SSH Access

Make sure you can SSH to the server:

```bash
# Test connection
ssh root@45.56.106.79

# Recommended: Set up SSH key
ssh-copy-id root@45.56.106.79
```

### 2. Server Directory Structure

On first run, set up the RePEc directory on your Linode server:

```bash
ssh root@45.56.106.79

# Create directory
mkdir -p /var/lib/repec/rdf

# Create archive metadata
cat > /var/lib/repec/rdf/bjnecon.rdf << 'EOF'
Template-Type: ReDIF-Archive 1.0
Handle: RePEc:bjn
Name: The Unjournal Evaluations
Maintainer-Email: contact@unjournal.org
Description: Open evaluations of research papers by The Unjournal
URL: https://unjournal.pubpub.org/
Maintainer-Name: The Unjournal
EOF

# Create series metadata
cat > /var/lib/repec/rdf/bjnevalua.rdf << 'EOF'
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

chmod 644 *.rdf
```

See **[docs/REPEC_DEPLOYMENT.md](../docs/REPEC_DEPLOYMENT.md)** for detailed server setup.

### 3. PubPub Credentials (Optional)

For public pubs, no credentials needed. To include unpublished pubs:

Create `tests/conf_settings.py`:
```python
community_url = "https://unjournal.pubpub.org"
community_id = "d28e8e57-7f59-486b-9395-b548158a27d6"
email = "your@email.com"
password = "your_password"
```

## Usage Examples

### Generate and Deploy

```bash
# Standard usage
./scripts/update_repec.sh

# Output:
# ✓ Using Python 3.13.5 from venv/
# Running RePEc generator...
# 📚 Fetching pubs from https://unjournal.pubpub.org...
# ✅ Generated 193 records
# 📤 Uploading to root@45.56.106.79...
# ✅ Complete!
```

### Generate Only

```bash
# Generate RDF file locally without deploying
./scripts/update_repec.sh --skip-deploy

# File created in: repec_rdfs/evalX_HHMMSS.rdf
```

### Dry Run

```bash
# See what would happen without making changes
./scripts/update_repec.sh --dry-run
```

### Custom Server

```bash
# Use different server settings
./scripts/update_repec.sh \
  --server my.server.com \
  --user repec \
  --remote-path /home/repec/archive/
```

## Files Generated

Each run creates:
- **Local**: `repec_rdfs/evalX_HHMMSS.rdf` (timestamped)
- **Server**: `/var/lib/repec/rdf/unjournal_eval_YYYYMMDD.rdf`
- **Server symlink**: `/var/lib/repec/rdf/latest.rdf` → current file

## Automation

### Weekly Cron Job

```bash
# Edit crontab
crontab -e

# Add this line (runs every Sunday at 2am)
0 2 * * 0 cd /path/to/pypubpub && ./scripts/update_repec.sh
```

### Manual Trigger

```bash
# Run anytime to update RePEc with latest evaluations
cd /path/to/pypubpub
./scripts/update_repec.sh
```

## Verification

### Check Generated File

```bash
# Count records
grep -c "^Template-Type: ReDIF-Paper 1.0" repec_rdfs/evalX_*.rdf

# View latest entries
tail -100 repec_rdfs/evalX_*.rdf
```

### Check Server

```bash
# List files on server
ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/"

# View latest file
ssh root@45.56.106.79 "cat /var/lib/repec/rdf/latest.rdf | head -50"
```

### Check RePEc Indexing

After deployment, RePEc will index within 24 hours:
- **Archive**: https://ideas.repec.org/s/bjn/evalua.html
- **Individual records**: https://ideas.repec.org/p/bjn/evalua/SLUG.html

### Check Google Scholar

After RePEc indexes (1-7 days), search on Google Scholar:
- https://scholar.google.com/
- Search for paper titles or DOIs
- Should show: "Published in The Unjournal"

## Troubleshooting

### Python Version Error

```
TypeError: unsupported operand type(s) for |: '_TypedDictMeta' and 'type'
```

**Solution**: Use Python 3.10+. The wrapper script handles this automatically.

### SSH Permission Denied

```
Permission denied (publickey,password)
```

**Solution**: Set up SSH key:
```bash
ssh-copy-id root@45.56.106.79
```

### No Records Generated

**Check**:
1. Internet connection
2. PubPub server is accessible
3. Credentials (if needed for unpublished pubs)

### SCP Failed

**Solution**:
1. Verify server directory exists: `ssh root@45.56.106.79 "ls -ld /var/lib/repec/rdf"`
2. Check permissions: `ssh root@45.56.106.79 "ls -la /var/lib/repec/rdf"`

## Advanced Options

```bash
# All options
./scripts/update_repec.sh \
  --dry-run              # Preview only
  --skip-deploy          # Generate but don't upload
  --output-dir ./output  # Custom output directory
  --server 45.56.106.79  # Custom server
  --user root            # Custom SSH user
  --remote-path /var/lib/repec/rdf/  # Custom remote path
```

## Related Documentation

- **[REPEC_DEPLOYMENT.md](../docs/REPEC_DEPLOYMENT.md)** - Complete deployment guide
- **[RePEc Registration](https://authors.repec.org/)** - Register your archive
- **[ReDIF Format](https://ideas.repec.org/t/rdf.html)** - Metadata format spec

## Support

For issues:
1. Check server logs: `ssh root@45.56.106.79 "tail -100 /var/log/syslog"`
2. Test SCP manually: `scp test.txt root@45.56.106.79:/var/lib/repec/rdf/`
3. Verify RePEc registration: https://authors.repec.org/
