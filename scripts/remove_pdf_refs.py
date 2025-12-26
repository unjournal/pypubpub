#!/usr/bin/env python3
"""
Remove PDF file references from RePEc RDF files.
PubPub /pdf URLs return 404, so we should only reference HTML versions.
"""

import sys

def remove_pdf_refs(input_file, output_file):
    """Remove PDF File-URL and File-Format lines from RDF file"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    skip_next = False
    pdf_count = 0
    
    for i, line in enumerate(lines):
        # If previous line was a PDF URL, skip this File-Format line
        if skip_next:
            skip_next = False
            continue
        
        # Check if this is a PDF URL
        if '/pdf' in line and line.strip().startswith('File-URL:'):
            # Skip this line and the next (File-Format)
            skip_next = True
            pdf_count += 1
            continue
        
        cleaned_lines.append(line)
    
    # Write cleaned file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    return pdf_count

def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_pdf_refs.py <input_rdf> [output_rdf]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.rdf', '_no_pdf.rdf')
    
    print(f"Removing PDF references from: {input_file}")
    pdf_count = remove_pdf_refs(input_file, output_file)
    print(f"Removed {pdf_count} PDF references")
    print(f"Output: {output_file}")

if __name__ == '__main__':
    main()
