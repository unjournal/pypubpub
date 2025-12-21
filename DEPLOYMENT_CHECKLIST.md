# RePEc Deployment Checklist

## ✅ Completed

- [x] Generated full RDF export from unjournal.pubpub.org (193 records)
- [x] Created incremental file `eval2025_04.rdf` (22 new records, 2025-47 to 2025-68)
- [x] Verified file format and content
- [x] Created deployment scripts and documentation

## 🔄 Ready to Deploy

The file **`repec_rdfs/eval2025_04.rdf`** is ready to upload to your Linode server.

### File Details
- **Records**: 22 evaluations
- **Number Range**: 2025-47 to 2025-68
- **Date Range**: July 2025 - December 2025
- **File Size**: 302 lines, ~15 KB
- **Latest Evaluation**: "Adjusting for Scale-Use Heterogeneity" (December 7, 2025)

## ⚠️ Action Required

### 1. Verify Linode Server Access

The SSH connection to `45.56.106.79` timed out. Please verify:

```bash
# Try connecting to your Linode server
ssh root@45.56.106.79

# If the IP has changed, check your Linode dashboard
# If you need a different user: ssh your-user@45.56.106.79
# If SSH is on a different port: ssh -p PORT root@45.56.106.79
```

**Possible issues**:
- [ ] IP address has changed (check Linode dashboard)
- [ ] SSH port is not 22 (check server config)
- [ ] Firewall blocking connection (check Linode network settings)
- [ ] Need to be on VPN or specific network
- [ ] SSH key not set up (try: `ssh-copy-id root@45.56.106.79`)

### 2. Upload the RDF File

Once you have SSH access, upload the file:

```bash
# Upload the new file
scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/

# If you use a different user/port:
# scp -P PORT repec_rdfs/eval2025_04.rdf your-user@45.56.106.79:/path/to/repec/rdf/
```

### 3. Verify Upload

```bash
# Check the file is on the server
ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/eval2025_04.rdf"

# Verify record count
ssh root@45.56.106.79 "grep -c '^Template-Type: ReDIF-Paper 1.0' /var/lib/repec/rdf/eval2025_04.rdf"
# Should show: 22

# View first record
ssh root@45.56.106.79 "head -30 /var/lib/repec/rdf/eval2025_04.rdf"
```

### 4. Check Server Directory Structure

Verify your RePEc directory has the correct structure:

```bash
ssh root@45.56.106.79 "ls -la /var/lib/repec/rdf/"
```

You should see:
```
bjnecon.rdf      # Archive metadata
bjnevalua.rdf    # Series metadata
eval2024_01.rdf
eval2024_02.rdf
eval2024_03.rdf
eval2025_01.rdf
eval2025_02.rdf
eval2025_03.rdf
eval2025_04.rdf  # ⭐ NEW FILE
```

If the directory doesn't exist or is empty, see "Server Setup" below.

### 5. Update Timestamp (Optional)

Tell RePEc there's new content:

```bash
ssh root@45.56.106.79 "touch /var/lib/repec/rdf/eval2025_04.rdf"
```

## 📋 Server Setup (If Needed)

If the RePEc directory doesn't exist on your server, set it up:

```bash
ssh root@45.56.106.79

# Create directory
mkdir -p /var/lib/repec/rdf
cd /var/lib/repec/rdf

# Create archive metadata
cat > bjnecon.rdf << 'EOF'
Template-Type: ReDIF-Archive 1.0
Handle: RePEc:bjn
Name: The Unjournal Evaluations
Maintainer-Email: contact@unjournal.org
Description: Open evaluations of research papers by The Unjournal
URL: https://unjournal.pubpub.org/
Maintainer-Name: The Unjournal
EOF

# Create series metadata
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

# Exit SSH
exit
```

Then upload all your existing RDF files:

```bash
scp repec_rdfs/eval2024_*.rdf root@45.56.106.79:/var/lib/repec/rdf/
scp repec_rdfs/eval2025_*.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

## 📊 Verification Timeline

After uploading:

- **Day 0** (Today): Upload complete ✅
- **Day 1**: RePEc crawler finds new files
- **Day 2**: Records appear on RePEc IDEAS
- **Day 7**: Google Scholar starts indexing
- **Day 14**: All records visible on Google Scholar

### Check RePEc Indexing

Visit: **https://ideas.repec.org/s/bjn/evalua.html**

You should see your evaluations listed, including new ones like:
- "Evaluation Summary: Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
- "Evaluation 1 of Adjusting for Scale-Use Heterogeneity..."
- "Evaluation 2 of Adjusting for Scale-Use Heterogeneity..."

### Check Google Scholar

Search for paper titles:
- "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
- "Does online fundraising increase charitable giving"
- "Irrigation Strengthens Climate Resilience"

Records should show:
- **Citation**: "Published in The Unjournal"
- **Link**: https://unjournal.pubpub.org/pub/...

## 🔧 Troubleshooting

### Can't Connect to Server

1. **Check IP**: Log into Linode dashboard, verify IP is `45.56.106.79`
2. **Check SSH port**: Try `ssh -p 2222 root@45.56.106.79` (common alternate)
3. **Check firewall**: Ensure port 22 is open in Linode firewall settings
4. **Use Linode console**: Access server via Linode web console (LISH)

### Directory Doesn't Exist

- See "Server Setup" section above
- Or check if RePEc files are in a different location: `ssh root@45.56.106.79 "find / -name 'bjnecon.rdf' 2>/dev/null"`

### RePEc Not Indexing

1. **Wait**: Initial crawl can take 24-48 hours
2. **Check registration**: Visit https://authors.repec.org/ and verify archive is registered
3. **Verify accessibility**: Make sure files are publicly accessible (HTTP/HTTPS)
4. **Contact RePEc**: Email RePEc support with your archive handle (RePEc:bjn)

### Google Scholar Not Showing

1. **Check RePEc first**: Must be on RePEc IDEAS before Google Scholar
2. **Wait longer**: Can take 1-2 weeks
3. **Check DOIs**: Verify all DOIs are registered with Crossref/DataCite
4. **Check robots.txt**: Ensure server allows crawlers

## 📝 Summary

**What's Ready**:
- ✅ New RDF file created: `repec_rdfs/eval2025_04.rdf`
- ✅ 22 new evaluation records (2025-47 to 2025-68)
- ✅ All recent evaluations included (up to December 2025)
- ✅ Documentation and scripts created

**What You Need to Do**:
1. ⚠️ Verify Linode server access (IP, port, credentials)
2. ⚠️ Upload `eval2025_04.rdf` to server
3. ⚠️ Verify file is on server
4. ⏳ Wait 24-48 hours for RePEc indexing
5. ⏳ Wait 1-2 weeks for Google Scholar

## 📚 Documentation

- **This file**: Deployment checklist and troubleshooting
- **REPEC_UPDATE_SUMMARY.md**: Complete summary of what was generated
- **docs/REPEC_DEPLOYMENT.md**: Full deployment guide
- **scripts/README_REPEC.md**: Scripts documentation

## 🔄 Future Updates

When you have more evaluations (2025-69+), run:

```bash
# Generate fresh data
venv/bin/python scripts/generate_and_deploy_repec.py --skip-deploy

# Extract next batch (adjust number >= 69 as needed)
# See REPEC_UPDATE_SUMMARY.md for extraction script

# Upload
scp repec_rdfs/eval2025_05.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

---

**Need Help?**
- Check server: `ssh root@45.56.106.79`
- Review docs: `cat docs/REPEC_DEPLOYMENT.md`
- Check existing files: `ls -la repec_rdfs/`
