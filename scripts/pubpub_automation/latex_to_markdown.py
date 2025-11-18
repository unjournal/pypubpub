#!/usr/bin/env python3
"""
LaTeX to Markdown Converter for Evaluation Reviews

Converts LaTeX evaluation reviews to PubPub-compatible markdown.
Handles common LaTeX commands, citations, math, and formatting.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class LatexToMarkdownConverter:
    """Converts LaTeX documents to markdown for PubPub."""

    def __init__(self):
        """Initialize converter with common LaTeX->Markdown mappings."""
        # Simple text formatting
        self.simple_replacements = [
            (r'\\textbf\{([^}]+)\}', r'**\1**'),  # Bold
            (r'\\textit\{([^}]+)\}', r'*\1*'),    # Italic
            (r'\\emph\{([^}]+)\}', r'*\1*'),      # Emphasis
            (r'\\texttt\{([^}]+)\}', r'`\1`'),    # Monospace
            (r'``', r'"'),                         # Opening quotes
            (r"''", r'"'),                         # Closing quotes
            (r'---', r'—'),                        # Em dash
            (r'--', r'–'),                         # En dash
            (r'\\\\ ', r'\n'),                     # Line breaks
            (r'\\noindent', r''),                  # No indent
            (r'\\vspace\{[^}]+\}', r'\n'),        # Vertical space
        ]

    def convert_file(self, latex_file: Path) -> str:
        """
        Convert a LaTeX file to markdown.

        Args:
            latex_file: Path to .tex file

        Returns:
            Markdown string
        """
        with open(latex_file, 'r', encoding='utf-8') as f:
            latex_content = f.read()

        return self.convert(latex_content)

    def convert(self, latex_content: str) -> str:
        """
        Convert LaTeX content to markdown.

        Args:
            latex_content: LaTeX string

        Returns:
            Markdown string
        """
        # Extract document body (between \begin{document} and \end{document})
        body_match = re.search(
            r'\\begin\{document\}(.*?)\\end\{document\}',
            latex_content,
            re.DOTALL
        )
        if body_match:
            content = body_match.group(1)
        else:
            content = latex_content

        # Remove comments
        content = re.sub(r'(?<!\\)%.*$', '', content, flags=re.MULTILINE)

        # Convert sections
        content = self._convert_sections(content)

        # Convert lists
        content = self._convert_lists(content)

        # Convert citations
        content = self._convert_citations(content)

        # Convert math
        content = self._convert_math(content)

        # Apply simple replacements
        for pattern, replacement in self.simple_replacements:
            content = re.sub(pattern, replacement, content)

        # Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', r'\n\n', content)

        # Clean up leading/trailing whitespace
        content = content.strip()

        return content

    def _convert_sections(self, content: str) -> str:
        """Convert LaTeX section commands to markdown headers."""
        # \section*{Title} -> ## Title
        content = re.sub(r'\\section\*\{([^}]+)\}', r'## \1', content)
        content = re.sub(r'\\section\{([^}]+)\}', r'## \1', content)

        # \subsection*{Title} -> ### Title
        content = re.sub(r'\\subsection\*\{([^}]+)\}', r'### \1', content)
        content = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', content)

        # \subsubsection*{Title} -> #### Title
        content = re.sub(r'\\subsubsection\*\{([^}]+)\}', r'#### \1', content)
        content = re.sub(r'\\subsubsection\{([^}]+)\}', r'#### \1', content)

        return content

    def _convert_lists(self, content: str) -> str:
        """Convert LaTeX enumerate and itemize to markdown lists."""
        # Enumerate (numbered lists)
        def convert_enumerate(match):
            items = match.group(1)
            # Extract \item entries
            item_list = re.findall(r'\\item(?:\[([^\]]+)\])?\s*([^\\]*(?:\\(?!item)[^\\]*)*)', items)
            md_items = []
            for i, (label, text) in enumerate(item_list, 1):
                if label:  # Custom label like \item[(a)]
                    md_items.append(f"{label} {text.strip()}")
                else:
                    md_items.append(f"{i}. {text.strip()}")
            return '\n'.join(md_items)

        content = re.sub(
            r'\\begin\{enumerate\}(.*?)\\end\{enumerate\}',
            convert_enumerate,
            content,
            flags=re.DOTALL
        )

        # Itemize (bullet lists)
        def convert_itemize(match):
            items = match.group(1)
            item_list = re.findall(r'\\item\s*([^\\]*(?:\\(?!item)[^\\]*)*)', items)
            md_items = [f"- {text.strip()}" for text in item_list]
            return '\n'.join(md_items)

        content = re.sub(
            r'\\begin\{itemize\}(.*?)\\end\{itemize\}',
            convert_itemize,
            content,
            flags=re.DOTALL
        )

        return content

    def _convert_citations(self, content: str) -> str:
        """Convert LaTeX citations to simple references."""
        # \cite{key} -> [key]
        content = re.sub(r'\\cite\{([^}]+)\}', r'[\1]', content)

        # Remove bibliography commands (we'll handle references separately)
        content = re.sub(r'\\bibliographystyle\{[^}]+\}', '', content)
        content = re.sub(r'\\bibliography\{[^}]+\}', '\n\n## References\n\n*See bibliography file*', content)

        return content

    def _convert_math(self, content: str) -> str:
        """Convert LaTeX math to markdown (limited support)."""
        # Inline math: $...$ stays as $...$
        # Display math: \[...\] -> $$...$$
        content = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', content, flags=re.DOTALL)

        # Display math: $$...$$ stays
        # equation environment -> $$...$$
        content = re.sub(
            r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}',
            r'$$\1$$',
            content,
            flags=re.DOTALL
        )

        return content

    def convert_with_metadata(
        self,
        latex_file: Path,
        title: Optional[str] = None,
        authors: Optional[List[str]] = None,
        reviewer: Optional[str] = None
    ) -> str:
        """
        Convert LaTeX file and add metadata header.

        Args:
            latex_file: Path to .tex file
            title: Paper title (extracted if None)
            authors: Paper authors (extracted if None)
            reviewer: Reviewer name (extracted if None)

        Returns:
            Markdown with metadata
        """
        # Convert main content
        markdown = self.convert_file(latex_file)

        # Extract metadata from LaTeX if not provided
        with open(latex_file, 'r') as f:
            latex_content = f.read()

        if not title:
            title_match = re.search(r'Review of [``\"]([^``\"]+)[``\"]', latex_content)
            if title_match:
                title = title_match.group(1)

        if not reviewer:
            reviewer_match = re.search(r'\\textbf\{Reviewer:\}.*?\\textit\{([^}]+)\}', latex_content)
            if reviewer_match:
                reviewer = reviewer_match.group(1)

        # Build metadata header
        header_parts = []
        if title:
            header_parts.append(f"# Review of \"{title}\"\n")
        if reviewer:
            header_parts.append(f"**Reviewer:** {reviewer}\n")

        if header_parts:
            return ''.join(header_parts) + '\n' + markdown

        return markdown


def main():
    """Example usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python latex_to_markdown.py <input.tex> [output.md]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.with_suffix('.md')

    converter = LatexToMarkdownConverter()
    markdown = converter.convert_with_metadata(input_file)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Converted {input_file} -> {output_file}")
    print(f"Output length: {len(markdown)} characters")


if __name__ == '__main__':
    main()
