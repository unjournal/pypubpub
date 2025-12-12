#!/usr/bin/env python3
"""
Generate HTML files for PubPub import.

PubPub's UI import feature properly converts HTML tables, so this script
generates HTML files that can be uploaded through the PubPub editor's
import functionality.

Usage:
    python generate_html_export.py --paper "Paper Name" --output evaluation_summary.html
"""

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def generate_html_for_pubpub(markdown_content: str, title: str = "Evaluation Summary") -> str:
    """
    Convert markdown with HTML tables to a full HTML document for PubPub import.

    PubPub's import accepts HTML and properly converts tables.
    """
    # Basic markdown to HTML conversion for non-table elements
    import re

    html_lines = []
    lines = markdown_content.split('\n')
    i = 0
    in_list = False

    while i < len(lines):
        line = lines[i]

        # Empty line
        if not line.strip():
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            i += 1
            continue

        # HTML table (pass through as-is)
        if line.strip().startswith('<table'):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # Collect entire table
            table_lines = [line]
            while i < len(lines) and '</table>' not in lines[i]:
                i += 1
                if i < len(lines):
                    table_lines.append(lines[i])
            html_lines.append('\n'.join(table_lines))
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            # Convert **bold** in headings
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            html_lines.append(f'<h{level}>{text}</h{level}>')
            i += 1
            continue

        # Bullet list
        if re.match(r'^[-*]\s+', line):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            item_text = re.sub(r'^[-*]\s+', '', line)
            item_text = convert_inline_markdown(item_text)
            html_lines.append(f'<li>{item_text}</li>')
            i += 1
            continue

        # Regular paragraph
        if in_list:
            html_lines.append('</ul>')
            in_list = False

        para_text = convert_inline_markdown(line)
        html_lines.append(f'<p>{para_text}</p>')
        i += 1

    if in_list:
        html_lines.append('</ul>')

    body_content = '\n'.join(html_lines)

    # Wrap in full HTML document
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
{body_content}
</body>
</html>"""

    return html_doc


def convert_inline_markdown(text: str) -> str:
    """Convert inline markdown (bold, italic, links) to HTML."""
    import re

    # Links [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

    # Italic *text*
    text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)

    return text


def generate_evaluation_html(paper_name: str, output_path: str = None) -> str:
    """
    Generate HTML file for a paper's evaluation summary.

    Args:
        paper_name: Name of the paper (partial match)
        output_path: Path to save HTML file (optional)

    Returns:
        HTML content string
    """
    from scripts.coda_integration.fetch_ratings import CodaRatingsFetcher
    from scripts.pubpub_automation.template_generator import TemplateGenerator

    # Fetch data
    fetcher = CodaRatingsFetcher()
    evals = fetcher.get_evaluations_for_paper(paper_name)

    if not evals:
        raise ValueError(f"No evaluations found for paper: {paper_name}")

    # Get paper info from first evaluation
    paper_info = {
        'title': evals[0].get('paper_name', paper_name),
        'authors': [],
        'doi': ''
    }

    # Build evaluations list
    evaluations = []
    for e in evals:
        evaluations.append({
            'name': e['evaluator_name'] or e['evaluator_code'] or 'Anonymous',
            'ratings': e['ratings'],
            'summary': e['summary'] or '*[Summary to be added]*'
        })

    # Generate markdown
    generator = TemplateGenerator()
    markdown = generator.generate_evaluation_summary(
        paper_info=paper_info,
        evaluations=evaluations
    )

    # Convert to HTML
    html = generate_html_for_pubpub(markdown, title=f"Evaluation Summary: {paper_info['title']}")

    # Save if path provided
    if output_path:
        Path(output_path).write_text(html, encoding='utf-8')
        print(f"HTML saved to: {output_path}")

    return html


def main():
    parser = argparse.ArgumentParser(description='Generate HTML for PubPub import')
    parser.add_argument('--paper', '-p', required=True, help='Paper name (partial match)')
    parser.add_argument('--output', '-o', default='evaluation_summary.html', help='Output file path')

    args = parser.parse_args()

    html = generate_evaluation_html(args.paper, args.output)
    print(f"\nGenerated {len(html)} characters of HTML")
    print(f"\nTo import into PubPub:")
    print(f"1. Open the pub in PubPub editor")
    print(f"2. Click the '+' menu or use Ctrl+/")
    print(f"3. Select 'Import' or drag-drop the HTML file")


if __name__ == '__main__':
    main()
