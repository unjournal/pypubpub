#!/usr/bin/env python3
"""
Convert Markdown to PubPub ProseMirror format.

PubPub uses ProseMirror as its document format. This module converts
basic markdown (headings, paragraphs, tables, lists) to ProseMirror JSON.
"""

import re
from typing import Dict, List, Any, Optional
import uuid


def generate_id() -> str:
    """Generate a unique node ID."""
    return 'n' + uuid.uuid4().hex[:11]


def create_text_node(text: str, marks: List[Dict] = None) -> Dict:
    """Create a text node."""
    node = {'type': 'text', 'text': text}
    if marks:
        node['marks'] = marks
    return node


def create_paragraph(content: List[Dict] = None, id: str = None) -> Dict:
    """Create a paragraph node."""
    return {
        'type': 'paragraph',
        'attrs': {
            'id': id or generate_id(),
            'class': None,
            'textAlign': None,
            'rtl': None,
            'suggestionId': None,
            'suggestionTimestamp': None,
            'suggestionUserId': None,
            'suggestionDiscussionId': None,
            'suggestionKind': None,
            'suggestionOriginalAttrs': None,
        },
        'content': content or []
    }


def create_heading(level: int, content: List[Dict], id: str = None) -> Dict:
    """Create a heading node."""
    return {
        'type': 'heading',
        'attrs': {
            'level': level,
            'fixedId': '',
            'id': id or generate_id(),
            'textAlign': None,
            'rtl': None,
            'suggestionId': None,
            'suggestionTimestamp': None,
            'suggestionUserId': None,
            'suggestionDiscussionId': None,
            'suggestionKind': None,
            'suggestionOriginalAttrs': None,
        },
        'content': content
    }


def create_table(rows: List[List[str]], header_row: bool = True) -> Dict:
    """Create a table node."""
    table_rows = []

    for i, row in enumerate(rows):
        cells = []
        for cell_text in row:
            cell = {
                'type': 'table_cell',
                'attrs': {
                    'colspan': 1,
                    'rowspan': 1,
                    'colwidth': None,
                    'background': None,
                },
                'content': [create_paragraph([create_text_node(cell_text.strip())])]
            }
            # Make header row bold
            if header_row and i == 0:
                cell['content'][0]['content'] = [
                    create_text_node(cell_text.strip(), [{'type': 'strong'}])
                ]
            cells.append(cell)

        table_rows.append({
            'type': 'table_row',
            'attrs': {},
            'content': cells
        })

    return {
        'type': 'table',
        'attrs': {
            'id': generate_id(),
            'hideLabel': False,
            'align': None,
            'size': None,
            'smallerFont': False,
            'suggestionId': None,
            'suggestionTimestamp': None,
            'suggestionUserId': None,
            'suggestionDiscussionId': None,
            'suggestionKind': None,
            'suggestionOriginalAttrs': None,
        },
        'content': table_rows
    }


def create_bullet_list(items: List[str]) -> Dict:
    """Create a bullet list node."""
    list_items = []
    for item in items:
        list_items.append({
            'type': 'list_item',
            'attrs': {},
            'content': [create_paragraph([create_text_node(item.strip())])]
        })

    return {
        'type': 'bullet_list',
        'attrs': {},
        'content': list_items
    }


def parse_html_cell_content(cell_html: str) -> List[Dict]:
    """Parse HTML cell content including <strong>, <em>, and links."""
    nodes = []
    pos = 0
    text = cell_html.strip()

    while pos < len(text):
        # Check for <strong> tag
        if text[pos:pos+8].lower() == '<strong>':
            end_tag = text.lower().find('</strong>', pos + 8)
            if end_tag != -1:
                bold_text = text[pos+8:end_tag]
                # Recursively parse inner content for nested tags
                inner_nodes = parse_html_cell_content(bold_text)
                for node in inner_nodes:
                    if 'marks' not in node:
                        node['marks'] = []
                    node['marks'].append({'type': 'strong'})
                nodes.extend(inner_nodes)
                pos = end_tag + 9
                continue

        # Check for <em> tag
        if text[pos:pos+4].lower() == '<em>':
            end_tag = text.lower().find('</em>', pos + 4)
            if end_tag != -1:
                italic_text = text[pos+4:end_tag]
                inner_nodes = parse_html_cell_content(italic_text)
                for node in inner_nodes:
                    if 'marks' not in node:
                        node['marks'] = []
                    node['marks'].append({'type': 'em'})
                nodes.extend(inner_nodes)
                pos = end_tag + 5
                continue

        # Check for <a href="..."> tag
        if text[pos:pos+2].lower() == '<a':
            # Find the href attribute
            href_match = re.search(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>', text[pos:], re.IGNORECASE)
            if href_match:
                href = href_match.group(1)
                tag_end = text.find('>', pos)
                if tag_end != -1:
                    close_tag = text.lower().find('</a>', tag_end)
                    if close_tag != -1:
                        link_text = text[tag_end+1:close_tag]
                        nodes.append(create_text_node(link_text, [{'type': 'link', 'attrs': {'href': href, 'title': None, 'target': None}}]))
                        pos = close_tag + 4
                        continue

        # Check for <br> or <br/>
        if text[pos:pos+4].lower() == '<br>' or text[pos:pos+5].lower() == '<br/>':
            # Add a hard break or just space
            nodes.append(create_text_node(' '))
            pos += 5 if text[pos:pos+5].lower() == '<br/>' else 4
            continue

        # Find next tag
        next_tag = text.find('<', pos)
        if next_tag == -1:
            next_tag = len(text)

        # Add plain text
        plain_text = text[pos:next_tag]
        if plain_text:
            nodes.append(create_text_node(plain_text))
        pos = next_tag

        # Safety: skip unknown tags
        if pos < len(text) and text[pos] == '<':
            tag_end = text.find('>', pos)
            if tag_end != -1:
                pos = tag_end + 1
            else:
                pos += 1

    return nodes if nodes else [create_text_node(text)]


def parse_html_table(html: str) -> Optional[Dict]:
    """Parse an HTML table into ProseMirror table node."""
    # Extract rows
    rows = []
    row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.IGNORECASE | re.DOTALL)
    cell_pattern = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.IGNORECASE | re.DOTALL)

    for row_match in row_pattern.finditer(html):
        row_html = row_match.group(1)
        cells = []
        for cell_match in cell_pattern.finditer(row_html):
            cell_content = cell_match.group(1).strip()
            cells.append(cell_content)
        if cells:
            rows.append(cells)

    if not rows:
        return None

    # Build ProseMirror table
    table_rows = []
    for i, row in enumerate(rows):
        table_cells = []
        for cell_html in row:
            # Parse cell content for formatting
            cell_nodes = parse_html_cell_content(cell_html)
            cell = {
                'type': 'table_cell',
                'attrs': {
                    'colspan': 1,
                    'rowspan': 1,
                    'colwidth': None,
                    'background': None,
                },
                'content': [create_paragraph(cell_nodes)]
            }
            table_cells.append(cell)

        table_rows.append({
            'type': 'table_row',
            'attrs': {},
            'content': table_cells
        })

    return {
        'type': 'table',
        'attrs': {
            'id': generate_id(),
            'hideLabel': False,
            'align': None,
            'size': None,
            'smallerFont': False,
            'suggestionId': None,
            'suggestionTimestamp': None,
            'suggestionUserId': None,
            'suggestionDiscussionId': None,
            'suggestionKind': None,
            'suggestionOriginalAttrs': None,
        },
        'content': table_rows
    }


def parse_inline_formatting(text: str) -> List[Dict]:
    """Parse inline formatting (bold, italic, links) in text."""
    nodes = []
    pos = 0

    while pos < len(text):
        # Check for markdown link [text](url)
        if text[pos] == '[':
            # Find the closing bracket
            bracket_end = text.find(']', pos + 1)
            if bracket_end != -1 and bracket_end + 1 < len(text) and text[bracket_end + 1] == '(':
                # Find the closing parenthesis
                paren_end = text.find(')', bracket_end + 2)
                if paren_end != -1:
                    link_text = text[pos + 1:bracket_end]
                    link_url = text[bracket_end + 2:paren_end]
                    # Create link node with href mark
                    nodes.append(create_text_node(link_text, [{'type': 'link', 'attrs': {'href': link_url, 'title': None, 'target': None}}]))
                    pos = paren_end + 1
                    continue

        # Check for bold **text**
        if text[pos:pos+2] == '**':
            end = text.find('**', pos + 2)
            if end != -1:
                bold_text = text[pos+2:end]
                nodes.append(create_text_node(bold_text, [{'type': 'strong'}]))
                pos = end + 2
                continue

        # Check for italic *text* (but not **)
        if text[pos] == '*' and (pos + 1 >= len(text) or text[pos+1] != '*'):
            end = text.find('*', pos + 1)
            if end != -1 and (end + 1 >= len(text) or text[end+1] != '*'):
                italic_text = text[pos+1:end]
                nodes.append(create_text_node(italic_text, [{'type': 'em'}]))
                pos = end + 1
                continue

        # Find next marker or end of string
        next_bold = text.find('**', pos)
        next_italic = -1
        next_link = text.find('[', pos)

        # Find italic that's not part of bold
        search_pos = pos
        while search_pos < len(text):
            idx = text.find('*', search_pos)
            if idx == -1:
                break
            if idx + 1 < len(text) and text[idx+1] == '*':
                search_pos = idx + 2
                continue
            if idx > 0 and text[idx-1] == '*':
                search_pos = idx + 1
                continue
            next_italic = idx
            break

        next_marker = len(text)
        if next_bold != -1 and next_bold < next_marker:
            next_marker = next_bold
        if next_italic != -1 and next_italic < next_marker:
            next_marker = next_italic
        if next_link != -1 and next_link < next_marker:
            next_marker = next_link

        # Add plain text up to next marker
        plain_text = text[pos:next_marker]
        if plain_text:
            nodes.append(create_text_node(plain_text))
        pos = next_marker

        # Safety: if we didn't advance, move forward by 1
        if pos < len(text) and plain_text == '':
            nodes.append(create_text_node(text[pos]))
            pos += 1

    return nodes if nodes else [create_text_node(text)]


def markdown_to_prosemirror(markdown: str, convert_html_tables: bool = False) -> Dict:
    """
    Convert markdown string to PubPub ProseMirror document format.

    Supports:
    - Headings (# ## ###)
    - Paragraphs
    - Markdown tables (| col | col |)
    - HTML tables (<table>...</table>) - kept as raw text by default
    - Bullet lists (- item)
    - Bold (**text**) and italic (*text*)
    - Links [text](url)

    Args:
        markdown: Markdown formatted string
        convert_html_tables: If True, convert HTML tables to ProseMirror table nodes.
                           If False (default), keep them as raw text in paragraphs.
                           Note: PubPub API may reject table nodes, so default is False.

    Returns:
        ProseMirror document dict
    """
    # First, extract HTML tables and replace with placeholders
    html_tables = []
    table_pattern = re.compile(r'<table[^>]*>.*?</table>', re.IGNORECASE | re.DOTALL)

    def replace_table(match):
        html_tables.append(match.group(0))
        return f'__HTML_TABLE_{len(html_tables) - 1}__'

    processed_markdown = table_pattern.sub(replace_table, markdown)

    lines = processed_markdown.split('\n')
    content = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Check for HTML table placeholder
        table_placeholder_match = re.match(r'^__HTML_TABLE_(\d+)__$', line.strip())
        if table_placeholder_match:
            table_idx = int(table_placeholder_match.group(1))
            if table_idx < len(html_tables):
                if convert_html_tables:
                    # Convert to ProseMirror table node
                    table_node = parse_html_table(html_tables[table_idx])
                    if table_node:
                        content.append(table_node)
                else:
                    # Keep as raw HTML text in a paragraph (PubPub API compatible)
                    # Compress whitespace in the HTML
                    html_text = ' '.join(html_tables[table_idx].split())
                    content.append(create_paragraph([create_text_node(html_text)]))
            i += 1
            continue

        # Heading
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2)
            content.append(create_heading(level, parse_inline_formatting(text)))
            i += 1
            continue

        # Markdown table (starts with |)
        if line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_line = lines[i].strip()
                # Skip separator line (|---|---|)
                if not re.match(r'^\|[-:\s|]+\|$', table_line):
                    # Parse cells
                    cells = [c.strip() for c in table_line.split('|')[1:-1]]
                    table_lines.append(cells)
                i += 1

            if table_lines:
                content.append(create_table(table_lines, header_row=True))
            continue

        # Bullet list (starts with - or *)
        if re.match(r'^[-*]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i]):
                item_text = re.sub(r'^[-*]\s+', '', lines[i])
                items.append(item_text)
                i += 1
            content.append(create_bullet_list(items))
            continue

        # Regular paragraph
        # Note: we check for list markers (- or * followed by space) not just *
        # since * can appear in inline formatting like **bold** or *italic*
        para_lines = []
        while i < len(lines) and lines[i].strip():
            stripped = lines[i].strip()
            # Stop if we hit a heading, table, list item, or HTML table placeholder
            if stripped.startswith('#') or stripped.startswith('|'):
                break
            if stripped.startswith('__HTML_TABLE_'):
                break
            # Check for list markers: - or * followed by whitespace
            if (stripped.startswith('- ') or stripped.startswith('* ') or
                stripped == '-' or stripped == '*'):
                break
            para_lines.append(lines[i])
            i += 1

        if para_lines:
            para_text = ' '.join(para_lines)
            content.append(create_paragraph(parse_inline_formatting(para_text)))

    return {
        'type': 'doc',
        'attrs': {
            'meta': {},
            'suggestionId': None,
            'suggestionTimestamp': None,
            'suggestionUserId': None,
            'suggestionDiscussionId': None,
            'suggestionKind': None,
            'suggestionOriginalAttrs': None,
        },
        'content': content
    }


def main():
    """Test the converter."""
    test_markdown = """# Evaluation Summary

This is a test paragraph with **bold** and *italic* text.

## Ratings Comparison

| Criterion | Evaluator 1 | Evaluator 2 |
|-----------|-------------|-------------|
| Overall Assessment | 90 (85-94) | 91 (78-94) |
| Methods | 85 (75-95) | 89 (79-95) |

## Key Points

- First point
- Second point
- Third point

### Conclusion

This is the final paragraph.
"""

    import json
    doc = markdown_to_prosemirror(test_markdown)
    print(json.dumps(doc, indent=2))


if __name__ == '__main__':
    main()
