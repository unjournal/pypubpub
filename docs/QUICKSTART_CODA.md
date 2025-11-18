# Coda Quick Start

## 1. Get API Key from Coda
- Go to: https://coda.io/account
- Generate API Token
- Copy it (keep secret!)

## 2. Create .env File

```bash
cd /Users/yosemite/githubs/pypubpub

# Create .env file (NEVER commit this!)
cat > .env << 'ENVEOF'
# Coda API Configuration
CODA_API_KEY=paste_your_actual_key_here
CODA_DOC_ID=_dOyXJoZ6imx
CODA_TABLE_ID=grid-xxxxx

# PubPub Configuration
PUBPUB_EMAIL=contact@unjournal.org
PUBPUB_PASSWORD=your_password_here
PUBPUB_COMMUNITY_ID=d28e8e57-7f59-486b-9395-b548158a27d6
PUBPUB_COMMUNITY_URL=https://unjournal.pubpub.org
ENVEOF

# Edit to add your real credentials
nano .env
```

⚠️ **NEVER commit .env to git!** It's already gitignored.

## 3. Install & Test

```bash
source .venv/bin/activate
pip install codaio python-dotenv
python scripts/coda_integration/test_coda_connection.py
```

## 4. Fetch Data

```bash
# Fetch for specific paper
python scripts/coda_integration/fetch_from_coda.py "Adjusting for Scale-Use Heterogeneity"

# Or fetch all
python scripts/coda_integration/fetch_from_coda.py
```

This creates:
- `evaluation_data/public/` - Safe to commit
- `evaluation_data/confidential/` - NEVER commit (gitignored)

Done! See [CODA_WORKFLOW.md](CODA_WORKFLOW.md) for details.
