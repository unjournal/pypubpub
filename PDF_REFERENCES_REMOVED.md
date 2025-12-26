# PDF References Removed from eval2025_03.rdf

## Issue

The `eval2025_03.rdf` file contained references to PDF URLs like:
```
File-URL: https://unjournal.pubpub.org/pub/e1naturalregeneration/pdf
File-Format: Application/pdf
```

These URLs return **404 Not Found** - the PDFs don't exist or aren't hosted.

## Solution

Removed all PDF references from `eval2025_03.rdf` using the `scripts/remove_pdf_refs.py` script.

## What Was Changed

**Before (each record had 2 File-URLs):**
```rdf
File-URL: https://unjournal.pubpub.org/pub/e1naturalregeneration
File-Format: text/html
File-URL: https://unjournal.pubpub.org/pub/e1naturalregeneration/pdf
File-Format: Application/pdf
```

**After (only HTML version):**
```rdf
File-URL: https://unjournal.pubpub.org/pub/e1naturalregeneration
File-Format: text/html
```

## Statistics

- **File:** repec_rdfs/eval2025_03.rdf
- **Records affected:** 33 (all records in the file)
- **PDF references removed:** 33
- **Backup:** repec_rdfs/archive/eval2025_03_with_pdfs.rdf

## Other Files

Checked all other RDF files - **only eval2025_03.rdf had PDF references**:

| File | Records | PDF Refs |
|------|---------|----------|
| eval_07_2023.rdf | 9 | 0 |
| eval2024_01.rdf | 9 | 0 |
| eval2024_02.rdf | 46 | 0 |
| eval2024_03.rdf | 18 | 0 |
| eval2025_01.rdf | 3 | 0 |
| eval2025_02.rdf | 7 | 0 |
| eval2025_03.rdf | 33 | **66 → 0** ✓ |
| eval2025_04.rdf | 22 | 0 |

## Script Created

`scripts/remove_pdf_refs.py` - Removes PDF file references from RePEc RDF files

**Usage:**
```bash
venv/bin/python scripts/remove_pdf_refs.py <input.rdf> [output.rdf]
```

**What it does:**
- Scans for File-URL lines containing "/pdf"
- Removes the PDF URL line and its corresponding File-Format line
- Preserves all other content

## Verification

```bash
# Check for PDF references (should return 0)
grep -c 'pdf' repec_rdfs/eval2025_03.rdf

# Check file has correct number of records
grep -c '^Template-Type:' repec_rdfs/eval2025_03.rdf  # Should be 33

# Verify only HTML references remain
grep 'File-URL:' repec_rdfs/eval2025_03.rdf | wc -l  # Should be 33
```

## Impact

✅ **Positive:**
- RePEc won't try to fetch non-existent PDFs
- Cleaner metadata
- Faster indexing (fewer failed requests)

❌ **No negative impact:**
- HTML versions are fully accessible
- All content is still available
- Google Scholar can still index from HTML

## Ready to Deploy

The updated `eval2025_03.rdf` file is ready for deployment alongside `eval2025_04.rdf`.
