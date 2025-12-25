#!/usr/bin/env python3
"""
Enrich RePEc RDF files with actual abstracts from PubPub content

This script:
1. Reads an existing RDF file
2. For each record, fetches the actual pub content from PubPub
3. Extracts a meaningful abstract
4. Regenerates the RDF file with proper abstracts

Usage:
    python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_04.rdf
"""

import sys
import re
import time
import argparse
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def extract_abstract_from_url(url, max_length=500):
    """
    Fetch a PubPub page and extract the abstract/summary

    Args:
        url: PubPub pub URL
        max_length: Maximum abstract length in characters

    Returns:
        Extracted abstract text or None
    """
    # Import here to avoid circular imports
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Warning: beautifulsoup4 not installed. Install with: pip install beautifulsoup4")
        return None

    try:
        # Remove /pdf or other suffixes if present
        clean_url = url.rstrip('/').split('/pdf')[0].split('/download')[0]
        print(f"  Fetching: {clean_url}")
        response = requests.get(clean_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for the "Abstract" heading on the page
        abstract_heading = None
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip().lower()
            if heading_text == 'abstract':
                abstract_heading = heading
                break

        if abstract_heading:
            # Get content after Abstract heading until next heading
            abstract_parts = []
            for sibling in abstract_heading.find_next_siblings():
                if sibling.name in ['h1', 'h2', 'h3']:
                    break  # Stop at next heading
                text = sibling.get_text(strip=True)
                if text and len(text) > 20:
                    abstract_parts.append(text)
                    if len(abstract_parts) >= 5:  # Max 5 paragraphs
                        break

            if abstract_parts:
                abstract = ' '.join(abstract_parts)
            else:
                return None
        else:
            # No Abstract heading found - return None so we use template
            return None

        # Clean up whitespace
        abstract = re.sub(r'\s+', ' ', abstract).strip()

        # Truncate if too long
        if len(abstract) > max_length:
            # Try to break at sentence
            sentences = re.split(r'[.!?]\s+', abstract[:max_length + 100])
            if len(sentences) > 1:
                abstract = '. '.join(sentences[:-1]) + '.'
            else:
                abstract = abstract[:max_length] + '...'

        return abstract if abstract else None

    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return None


def parse_rdf_file(rdf_path):
    """
    Parse an RDF file into individual records

    Returns:
        List of record dicts with keys: title, authors, abstract, doi, url, etc.
    """
    with open(rdf_path, 'r') as f:
        content = f.read()

    # Split into records
    records = []
    current_record = {}

    for line in content.split('\n'):
        line = line.rstrip()

        if line.startswith('Template-Type:'):
            # Start new record
            if current_record:
                records.append(current_record)
            current_record = {'raw_lines': [line]}
        elif current_record:
            current_record['raw_lines'].append(line)

            # Parse key fields
            if line.startswith('Title: '):
                current_record['title'] = line[7:]
            elif line.startswith('Abstract: '):
                current_record['abstract'] = line[10:]
            elif line.startswith('File-URL: '):
                current_record['url'] = line[10:]
            elif line.startswith('Author-Name: '):
                if 'authors' not in current_record:
                    current_record['authors'] = []
                current_record['authors'].append(line[13:])
            elif line.startswith('Number: '):
                current_record['number'] = line[8:]

    # Add last record
    if current_record:
        records.append(current_record)

    return records


def enrich_record_abstract(record, force=False):
    """
    Enrich a record with actual abstract from PubPub

    Args:
        record: Record dict
        force: If True, fetch even if abstract exists

    Returns:
        Updated record dict
    """
    current_abstract = record.get('abstract', '')

    # Check if abstract needs enrichment
    needs_enrichment = (
        force or
        not current_abstract or
        current_abstract == 'None' or
        current_abstract.strip() == '' or
        'for The Unjournal.' in current_abstract  # Generic template text
    )

    if not needs_enrichment:
        print(f"  Skipping (has abstract): {record.get('title', 'Unknown')[:60]}")
        return record

    url = record.get('url')
    if not url:
        print(f"  No URL for: {record.get('title', 'Unknown')[:60]}")
        return record

    print(f"  Enriching: {record.get('title', 'Unknown')[:60]}")

    # Fetch abstract
    abstract = extract_abstract_from_url(url)

    if abstract:
        # Update the record
        record['abstract'] = abstract
        record['enriched'] = True
        print(f"    ✓ Got abstract ({len(abstract)} chars)")
    else:
        print(f"    ✗ Could not extract abstract")
        record['enriched'] = False

    # Rate limit
    time.sleep(2)  # Be nice to the server

    return record


def rebuild_rdf_record(record):
    """
    Rebuild RDF record text with updated abstract

    Returns:
        RDF text for this record
    """
    lines = []

    for line in record['raw_lines']:
        if line.startswith('Abstract: '):
            # Replace with enriched abstract
            if record.get('enriched') and 'abstract' in record:
                lines.append(f"Abstract: {record['abstract']}")
            else:
                lines.append(line)  # Keep original
        else:
            lines.append(line)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Enrich RePEc RDF files with actual abstracts from PubPub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enrich a specific file
  python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_04.rdf

  # Force re-fetch all abstracts
  python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_04.rdf --force

  # Dry run (don't write file)
  python scripts/enrich_repec_abstracts.py repec_rdfs/eval2025_04.rdf --dry-run
        """
    )

    parser.add_argument('rdf_file', help='RDF file to enrich')
    parser.add_argument('--force', action='store_true',
                       help='Re-fetch abstracts even if they exist')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without writing file')
    parser.add_argument('--output', help='Output file (default: overwrites input)')
    parser.add_argument('--limit', type=int,
                       help='Only process first N records (for testing)')

    args = parser.parse_args()

    print("=" * 70)
    print("📚 RePEc Abstract Enricher")
    print("=" * 70)

    # Parse RDF file
    print(f"\n📖 Reading: {args.rdf_file}")
    records = parse_rdf_file(args.rdf_file)
    print(f"   Found {len(records)} records")

    if args.limit:
        print(f"   Limiting to first {args.limit} records")
        records = records[:args.limit]

    # Enrich abstracts
    print(f"\n🔍 Enriching abstracts...")
    enriched_count = 0
    skipped_count = 0

    for i, record in enumerate(records, 1):
        print(f"\n[{i}/{len(records)}] {record.get('number', 'N/A')}")

        if args.dry_run:
            print(f"  DRY RUN - Would fetch: {record.get('url', 'No URL')}")
            continue

        record = enrich_record_abstract(record, force=args.force)

        if record.get('enriched'):
            enriched_count += 1
        else:
            skipped_count += 1

    if args.dry_run:
        print(f"\n✓ DRY RUN complete (no changes made)")
        return 0

    # Rebuild RDF file
    print(f"\n📝 Rebuilding RDF file...")
    output_lines = []

    for i, record in enumerate(records):
        if i > 0:
            output_lines.append('')  # Blank line between records
            output_lines.append('')
        output_lines.append(rebuild_rdf_record(record))

    output_content = '\n'.join(output_lines)

    # Write output
    output_file = args.output or args.rdf_file

    if output_file == args.rdf_file:
        # Backup original
        backup_file = args.rdf_file + '.backup'
        print(f"   Backing up original to: {backup_file}")
        import shutil
        shutil.copy2(args.rdf_file, backup_file)

    print(f"   Writing to: {output_file}")
    with open(output_file, 'w') as f:
        f.write(output_content)

    # Summary
    print("\n" + "=" * 70)
    print("✅ Complete!")
    print("=" * 70)
    print(f"  Records processed: {len(records)}")
    print(f"  Abstracts enriched: {enriched_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Output file: {output_file}")

    if enriched_count > 0:
        print(f"\n💡 Review the abstracts and deploy when ready:")
        print(f"   scp {output_file} root@45.56.106.79:/var/lib/repec/rdf/")

    return 0


if __name__ == '__main__':
    sys.exit(main())
