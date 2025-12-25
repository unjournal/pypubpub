# RePEc Update Summary - December 2025

## What's Been Created

### New RDF File
- **File**: `repec_rdfs/eval2025_04.rdf`
- **Records**: 22 evaluation records
- **Range**: Numbers 2025-47 through 2025-68
- **Date Range**: July 2025 - December 2025
- **File Size**: 302 lines

### Latest Evaluations Included

The new file includes the most recent evaluations:

1. **Asymmetry in Civic Information** (Togo tax participation) - July 2025
2. **Social Safety Nets and Women's Agency** - July 2025
3. **Ends versus Means: Kantians, Utilitarians** - August 2025
4. **Irrigation and Climate Resilience in Mali** - September 2025
5. **Online Fundraising and Charitable Giving** (Facebook experiment) - September 2025
6. **Adjusting for Scale-Use Heterogeneity** (Well-being) - November-December 2025 ⭐ **Most recent**

## Deployment Options

### Option 1: Manual SCP (Recommended for First Time)

```bash
# Copy the new file to Linode
scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/

# Verify it's there
ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/eval2025_04.rdf"
```

### Option 2: Using the Automated Script

```bash
# The script was designed for full regeneration, not incremental files
# You can manually specify which file to upload:

scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

## Server Directory Structure

Your Linode server should have:

```
/var/lib/repec/rdf/
├── bjnecon.rdf          # Archive metadata
├── bjnevalua.rdf        # Series metadata
├── eval2024_01.rdf      # Historical records
├── eval2024_02.rdf
├── eval2024_03.rdf
├── eval2025_01.rdf      # 2025-01 to 2025-03
├── eval2025_02.rdf      # 2025-05 to 2025-10
├── eval2025_03.rdf      # 2025-14 to 2025-46
└── eval2025_04.rdf      # 2025-47 to 2025-68 ⭐ NEW
```

## Verification Steps

### 1. Check File on Server
```bash
ssh root@45.56.106.79 "cat /var/lib/repec/rdf/eval2025_04.rdf | head -30"
```

### 2. Verify Record Count
```bash
ssh root@45.56.106.79 "grep -c '^Template-Type: ReDIF-Paper 1.0' /var/lib/repec/rdf/eval2025_04.rdf"
# Should return: 22
```

### 3. Check RePEc Indexing (After 24 Hours)

Visit: https://ideas.repec.org/s/bjn/evalua.html

Look for new records like:
- "Evaluation Summary: Adjusting for Scale-Use Heterogeneity..."
- "Evaluation 1 of Adjusting for Scale-Use Heterogeneity..."
- etc.

### 4. Check Google Scholar (After 1-7 Days)

Search for paper titles like:
- "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
- "Does online fundraising increase charitable giving"

Records should appear with:
- Citation: "Published in The Unjournal"
- Links to unjournal.pubpub.org

## Timeline for Indexing

1. **Upload**: Immediate
2. **RePEc Crawl**: Within 24 hours (automated crawler)
3. **RePEc IDEAS Display**: Shortly after crawl completes
4. **Google Scholar**: 1-7 days after RePEc indexes

## Next Steps

1. **Upload the file** to your Linode server:
   ```bash
   scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/
   ```

2. **Verify upload**:
   ```bash
   ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/eval2025_04.rdf"
   ```

3. **Wait for RePEc indexing** (24 hours)

4. **Check RePEc IDEAS**: https://ideas.repec.org/s/bjn/evalua.html

5. **Monitor Google Scholar** for new citations (1 week)

## Future Updates

When you have more evaluations (2025-69+), create `eval2025_05.rdf`:

```bash
# Regenerate full RDF
venv/bin/python scripts/generate_and_deploy_repec.py --skip-deploy

# Extract new records (adjust number range as needed)
python3 << 'EOF'
import re

input_file = 'repec_rdfs/evalX_HHMMSS.rdf'  # Use latest generated file
output_file = 'repec_rdfs/eval2025_05.rdf'

with open(input_file, 'r') as f:
    content = f.read()

records = content.split('\n\nTemplate-Type: ReDIF-Paper 1.0\n')
new_records = []

for i, record in enumerate(records):
    if i == 0 and record.startswith('Template-Type:'):
        full_record = record
    else:
        full_record = 'Template-Type: ReDIF-Paper 1.0\n' + record

    match = re.search(r'^Number: 2025-(\d+)$', full_record, re.MULTILINE)
    if match:
        num = int(match.group(1))
        if num >= 69:  # Adjust this number for next batch
            new_records.append(full_record)

with open(output_file, 'w') as f:
    f.write('\n\n'.join(new_records))

print(f"Created {output_file} with {len(new_records)} records")
EOF

# Then upload
scp repec_rdfs/eval2025_05.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

## Automated Monthly Updates

Consider setting up a cron job to regenerate and upload monthly:

```bash
# Add to crontab (runs first of every month at 2am)
0 2 1 * * cd /path/to/pypubpub && /path/to/pypubpub/scripts/update_repec.sh
```

## Files Generated

All files are in `repec_rdfs/`:
- ✅ `eval2025_04.rdf` - **Ready to deploy** (22 records, 2025-47 to 2025-68)
- 📄 `evalX_13_50_40.rdf` - Full export (193 records, all time) - Reference only
- 📄 `eval2025_03.rdf` - Previous file (already on server)

## Documentation

- **Complete Guide**: `docs/REPEC_DEPLOYMENT.md`
- **Scripts README**: `scripts/README_REPEC.md`
- **Main Script**: `scripts/generate_and_deploy_repec.py`
- **Wrapper**: `scripts/update_repec.sh`

## Questions?

- Check server connectivity: `ssh root@45.56.106.79`
- Verify RePEc registration: https://authors.repec.org/
- Check current RePEc listings: https://ideas.repec.org/s/bjn/evalua.html
- Review logs: `ssh root@45.56.106.79 "tail -100 /var/log/syslog"`
