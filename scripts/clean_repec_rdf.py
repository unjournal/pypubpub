#!/usr/bin/env python3
"""
Clean RePEc RDF files:
1. Fix Unicode issues (convert smart quotes, etc. to ASCII)
2. Add placeholder abstracts where missing
"""

import sys
import re
from pathlib import Path

def clean_unicode(text):
    """Replace problematic Unicode characters with ASCII equivalents"""
    replacements = {
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote / apostrophe
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2013': '-',  # En dash
        '\u2014': '--', # Em dash
        '\u2026': '...', # Ellipsis
        '\u00a0': ' ',  # Non-breaking space
        '\u00e2': '',   # â (common encoding issue)
        'â': "'",       # Common smart quote corruption
        'â': '"',       # Common smart quote corruption  
        'Â': '',        # Common encoding artifact
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Remove any remaining non-ASCII characters
    text = text.encode('ascii', errors='ignore').decode('ascii')
    
    return text

def parse_rdf_file(rdf_path):
    """Parse RDF file into records"""
    with open(rdf_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    records = []
    current_record = {}
    
    for line in content.split('\n'):
        line = line.rstrip()
        
        if line.startswith('Template-Type:'):
            if current_record:
                records.append(current_record)
            current_record = {'raw_lines': [line]}
        elif current_record:
            current_record['raw_lines'].append(line)
            
            # Parse key fields
            if line.startswith('Title: '):
                current_record['title'] = line[7:]
            elif line.startswith('Abstract:'):
                # Handle both "Abstract: text" and "Abstract:" (empty)
                current_record['abstract'] = line[10:] if len(line) > 10 else ''
    
    if current_record:
        records.append(current_record)
    
    return records

def get_placeholder_abstract(title):
    """Generate placeholder abstract for records without abstracts"""
    # Check if this is an author response
    is_author_response = title.lower().startswith("author") and "response" in title.lower()

    # Extract paper title from evaluation title
    if 'of "' in title:
        paper_title = title.split('of "')[1].rstrip('"')
    elif ': "' in title:
        paper_title = title.split(': "')[1].rstrip('"')
    else:
        paper_title = "this paper"

    if is_author_response:
        return f'This is an author response to the Unjournal\'s evaluation(s) of the paper "{paper_title}". Please see the discussion below.'
    else:
        return f'This is an evaluation of the paper "{paper_title}" for The Unjournal. Please see the discussion below.'

def clean_record(record):
    """Clean a single record - fix Unicode and add placeholder if needed"""
    title = record.get('title', '')
    abstract = record.get('abstract', '')

    # Check if abstract is missing or just "None"
    needs_placeholder = (
        abstract is None or
        abstract.strip() == '' or
        abstract.strip() == 'None' or
        abstract.startswith('Evaluation Summary and Metrics:') or
        abstract.startswith('Evaluation of "')
    )
    
    if needs_placeholder:
        placeholder = get_placeholder_abstract(title)
        record['new_abstract'] = placeholder
        record['needs_update'] = True
    else:
        record['needs_update'] = False
    
    # Clean Unicode in all lines
    cleaned_lines = []
    for line in record['raw_lines']:
        if line.startswith('Abstract:'):
            if record.get('needs_update'):
                cleaned_lines.append(f"Abstract: {clean_unicode(record['new_abstract'])}")
            else:
                # Just clean the existing abstract
                cleaned_lines.append(clean_unicode(line))
        else:
            cleaned_lines.append(clean_unicode(line))
    
    record['cleaned_lines'] = cleaned_lines
    return record

def main():
    if len(sys.argv) < 2:
        print("Usage: python clean_repec_rdf.py <input_rdf> [output_rdf]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.rdf', '_cleaned.rdf')
    
    print(f"Reading: {input_file}")
    records = parse_rdf_file(input_file)
    print(f"Found {len(records)} records")
    
    print("\nCleaning records...")
    cleaned_count = 0
    placeholder_count = 0
    
    for i, record in enumerate(records, 1):
        record = clean_record(record)
        if record.get('needs_update'):
            placeholder_count += 1
            print(f"  [{i}] Added placeholder: {record.get('title', 'Unknown')[:60]}")
        cleaned_count += 1
    
    # Write output
    print(f"\nWriting to: {output_file}")
    with open(output_file, 'w', encoding='ascii') as f:
        for i, record in enumerate(records):
            if i > 0:
                f.write('\n\n')
            f.write('\n'.join(record['cleaned_lines']))
    
    print(f"\nComplete!")
    print(f"  Records cleaned: {cleaned_count}")
    print(f"  Placeholders added: {placeholder_count}")
    print(f"  Output: {output_file}")

if __name__ == '__main__':
    main()
