# Setting Up Coda API Access

## Step 1: Get Your Coda API Key

1. Go to https://coda.io/account
2. Navigate to the **API Settings** section
3. Click **Generate API token**
4. Copy the token (it looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
5. Paste it into `.env` as `CODA_API_KEY`

⚠️ **Keep this secret!** Never commit this to git (it's already in .gitignore)

## Step 2: Find Your Document ID

1. Open your Coda document (the one with the evaluations table)
2. Look at the URL in your browser:
   ```
   https://coda.io/d/_dOyXJoZ6imx#All-unfinished-current-Tasks_tuXFw
                      ^^^^^^^^^^^
                      This is your doc ID
   ```
3. Copy the part after `/d/` (including the `_d` prefix)
4. Paste it into `.env` as `CODA_DOC_ID`

## Step 3: Find Your Table ID

### Option A: Use the Setup Script (Recommended)

```bash
cd scripts/coda_integration
python setup_coda.py
```

This will:
- Connect to your Coda account
- List all your documents
- Show all tables in your selected document
- Display table IDs and sample data
- Help you confirm you have the right table

### Option B: Manual Method

1. Open the table in Coda
2. Click the table menu (⋮) → **Copy table link**
3. The link contains the table ID:
   ```
   https://coda.io/d/_dOyXJoZ6imx/Evaluations_suABC123
                                              ^^^^^^^^
                                              This is the table ID
   ```
4. Paste it into `.env` as `CODA_TABLE_ID`

## Step 4: Test the Connection

```bash
cd scripts/coda_integration
python test_coda_connection.py
```

This will:
- Verify your API key works
- Check document access
- Show sample data from the table
- Confirm all fields are accessible

## Your .env File Should Look Like:

```bash
CODA_API_KEY=a1b2c3d4-1234-5678-9abc-def012345678
CODA_DOC_ID=_dOyXJoZ6imx
CODA_TABLE_ID=grid-suABC123XYZ
```

## Security Notes

- ✅ `.env` is in `.gitignore` - won't be committed
- ✅ Scripts use environment variables only
- ✅ Sensitive data stored in `evaluation_data/confidential/` (also gitignored)
- ⚠️ Never share your API key
- ⚠️ Never commit `.env` to git

## Troubleshooting

### "CODA_API_KEY environment variable not set"

Make sure you've created `.env` in the repository root (not in a subdirectory).

### "403 Forbidden" or "401 Unauthorized"

- Check your API key is correct
- Make sure you have access to the document
- Try regenerating your API token in Coda

### "Table not found"

- Verify the table ID is correct
- Use `setup_coda.py` to list all available tables
- Check you have permission to access the table

## Next Steps

Once your `.env` is configured:

1. Test connection: `python scripts/coda_integration/test_coda_connection.py`
2. Fetch data: `python scripts/coda_integration/fetch_from_coda.py`
3. Create packages: Use `create_package_from_data.py` with `create_from_coda()`

## See Also

- `QUICKSTART_CODA.md` - Quick 5-step guide
- `.env.example` - Template with all options
- `scripts/coda_integration/README.md` - Integration details
