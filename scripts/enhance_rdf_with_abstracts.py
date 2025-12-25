#!/usr/bin/env python3
"""
Enhance RePEc RDF file with actual abstracts from PubPub content

This script:
1. Reads an existing RDF file
2. Fetches actual abstract content from each pub's web page
3. Replaces generic abstracts with real content
4. Writes enhanced RDF file
"""

import re
import sys
import time
import argparse
from pathlib import Path

# For WebFetch simulation - we'll need to use requests + BeautifulSoup
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup


def extract_abstract_from_html(html_content):
    """Extract meaningful abstract from PubPub HTML content"""
    soup = BeautifulSoup(html_content, 'lxml')

    # Remove script, style, nav elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer']):
        element.decompose()

    # Look for the main content area
    main_content = soup.find('main') or soup.find('article') or soup.find(class_='pub-body')

    if not main_content:
        # Fallback to body
        main_content = soup.find('body')

    if not main_content:
        return None

    # Get all paragraphs
    paragraphs = main_content.find_all('p')

    # Filter out very short paragraphs and common boilerplate
    meaningful_paragraphs = []
    skip_phrases = [
        'subscribe', 'newsletter', 'cookie', 'privacy policy',
        'terms of service', 'all rights reserved', 'copyright',
        'follow us', 'share this', 'download pdf'
    ]

    for p in paragraphs:
        text = p.get_text().strip()
        if len(text) < 50:  # Skip very short paragraphs
            continue
        if any(phrase in text.lower() for phrase in skip_phrases):
            continue
        meaningful_paragraphs.append(text)

    if not meaningful_paragraphs:
        return None

    # Take first 2-3 paragraphs as abstract
    # But limit total length to ~500 characters
    abstract_parts = []
    total_length = 0
    max_length = 500

    for para in meaningful_paragraphs[:4]:
        if total_length + len(para) > max_length:
            # Add truncated version
            remaining = max_length - total_length
            if remaining > 100:
                abstract_parts.append(para[:remaining] + "...")
            break
        abstract_parts.append(para)
        total_length += len(para)

        # Stop if we have enough content
        if total_length > 300:
            break

    return ' '.join(abstract_parts) if abstract_parts else None


def fetch_abstract_from_url(url, max_retries=3):
    """Fetch and extract abstract from a PubPub URL"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            abstract = extract_abstract_from_html(response.text)
            return abstract

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} after error: {e}")
                time.sleep(2)
            else:
                print(f"  Failed to fetch after {max_retries} attempts: {e}")
                return None


def parse_rdf_file(file_path):
    """Parse RDF file into list of records"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Split into records
    records = []
    parts = content.split('\n\nTemplate-Type: ReDIF-Paper 1.0\n')

    for i, part in enumerate(parts):
        if i == 0 and part.startswith('Template-Type:'):
            records.append(part)
        elif part.strip():
            records.append('Template-Type: ReDIF-Paper 1.0\n' + part)

    return records


def extract_record_fields(record):
    """Extract key fields from an RDF record"""
    fields = {}

    # Extract File-URL
    url_match = re.search(r'^File-URL:\s*(.+)$', record, re.MULTILINE)
    if url_match:
        fields['url'] = url_match.group(1).strip()

    # Extract current abstract
    abstract_match = re.search(r'^Abstract:\s*(.*)$', record, re.MULTILINE)
    if abstract_match:
        fields['abstract'] = abstract_match.group(1).strip()

    # Extract title
    title_match = re.search(r'^Title:\s*(.+)$', record, re.MULTILINE)
    if title_match:
        fields['title'] = title_match.group(1).strip()

    # Extract number
    number_match = re.search(r'^Number:\s*(.+)$', record, re.MULTILINE)
    if number_match:
        fields['number'] = number_match.group(1).strip()

    return fields


def update_record_abstract(record, new_abstract):
    """Replace abstract in record with new content"""
    # Find and replace the Abstract line
    new_record = re.sub(
        r'^Abstract:.*$',
        f'Abstract: {new_abstract}',
        record,
        count=1,
        flags=re.MULTILINE
    )
    return new_record


def enhance_rdf_file(input_file, output_file, skip_existing=True, rate_limit=2):
    """
    Enhance RDF file with real abstracts

    Args:
        input_file: Path to input RDF file
        output_file: Path to output RDF file
        skip_existing: Skip records that already have non-generic abstracts
        rate_limit: Seconds to wait between requests
    """
    print(f"Reading {input_file}...")
    records = parse_rdf_file(input_file)
    print(f"Found {len(records)} records")

    enhanced_records = []
    stats = {'total': len(records), 'enhanced': 0, 'skipped': 0, 'failed': 0}

    for i, record in enumerate(records):
        fields = extract_record_fields(record)
        number = fields.get('number', f'#{i+1}')
        title = fields.get('title', 'Unknown')[:60]

        print(f"\n[{i+1}/{len(records)}] Processing {number}: {title}...")

        current_abstract = fields.get('abstract', '')

        # Check if abstract needs enhancement
        generic_patterns = [
            'Evaluation of',
            'Evaluation Summary and Metrics',
            'for The Unjournal',
            'Abstract: None',
            'Abstract: \n',
            'Abstract: $'
        ]

        is_generic = (
            not current_abstract or
            current_abstract == 'None' or
            len(current_abstract) < 50 or
            any(pattern in current_abstract for pattern in generic_patterns)
        )

        if skip_existing and not is_generic:
            print(f"  ✓ Already has abstract ({len(current_abstract)} chars)")
            enhanced_records.append(record)
            stats['skipped'] += 1
            continue

        # Fetch new abstract
        url = fields.get('url')
        if not url:
            print(f"  ⚠ No URL found, keeping original")
            enhanced_records.append(record)
            stats['skipped'] += 1
            continue

        print(f"  Fetching from: {url}")
        new_abstract = fetch_abstract_from_url(url, max_retries=2)

        if new_abstract:
            print(f"  ✓ Got abstract ({len(new_abstract)} chars)")
            enhanced_record = update_record_abstract(record, new_abstract)
            enhanced_records.append(enhanced_record)
            stats['enhanced'] += 1
        else:
            print(f"  ✗ Failed to fetch, keeping original")
            enhanced_records.append(record)
            stats['failed'] += 1

        # Rate limiting
        if i < len(records) - 1:
            time.sleep(rate_limit)

    # Write output file
    print(f"\nWriting to {output_file}...")
    with open(output_file, 'w') as f:
        f.write('\n\n'.join(enhanced_records))

    print(f"\n{'='*60}")
    print(f"Enhancement complete!")
    print(f"{'='*60}")
    print(f"Total records:     {stats['total']}")
    print(f"Enhanced:          {stats['enhanced']}")
    print(f"Already good:      {stats['skipped']}")
    print(f"Failed:            {stats['failed']}")
    print(f"\nOutput: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Enhance RePEc RDF file with real abstracts from PubPub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enhance eval2025_04.rdf
  python scripts/enhance_rdf_with_abstracts.py repec_rdfs/eval2025_04.rdf

  # Specify custom output file
  python scripts/enhance_rdf_with_abstracts.py input.rdf -o output.rdf

  # Force re-fetch all abstracts
  python scripts/enhance_rdf_with_abstracts.py input.rdf --no-skip-existing
        """
    )

    parser.add_argument('input_file', help='Input RDF file path')
    parser.add_argument('-o', '--output', help='Output RDF file (default: <input>_enhanced.rdf)')
    parser.add_argument('--no-skip-existing', action='store_true',
                       help='Re-fetch all abstracts, even for records with existing ones')
    parser.add_argument('--rate-limit', type=float, default=2,
                       help='Seconds to wait between requests (default: 2)')

    args = parser.parse_args()

    input_file = Path(args.input_file)
    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        return 1

    # Determine output file
    if args.output:
        output_file = Path(args.output)
    else:
        output_file = input_file.parent / f"{input_file.stem}_enhanced{input_file.suffix}"

    try:
        enhance_rdf_file(
            input_file,
            output_file,
            skip_existing=not args.no_skip_existing,
            rate_limit=args.rate_limit
        )
        return 0
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
