#!/usr/bin/env python3
"""
Evaluation Package Assembler

Assembles complete evaluation packages from various data sources:
- Coda form submissions
- LaTeX/Word documents
- PDF ratings
- Manual data entry

Outputs markdown documents ready for PubPub import.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

from .latex_to_markdown import LatexToMarkdownConverter
from .template_generator import TemplateGenerator
from .ratings_table_generator import generate_full_evaluation_ratings


@dataclass
class PaperMetadata:
    """Metadata about the paper being evaluated."""
    title: str
    authors: Union[List[str], str]
    doi: Optional[str] = None
    url: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'title': self.title,
            'authors': self.authors if isinstance(self.authors, list) else [self.authors],
            'doi': self.doi,
            'url': self.url,
            'abstract': self.abstract,
            'year': self.year
        }


@dataclass
class EvaluationData:
    """Data for a single evaluation."""
    ratings: Dict[str, Union[Dict, float, int, str]]
    review_text: Optional[str] = None
    evaluator_name: Optional[str] = None
    evaluator_affiliation: Optional[str] = None
    evaluator_orcid: Optional[str] = None
    is_public: bool = False  # Whether evaluator identity is public
    comments: Optional[str] = None

    # Source information
    review_source_type: Optional[str] = None  # 'latex', 'word', 'markdown', 'text'
    review_source_path: Optional[Path] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'name': self.evaluator_name,
            'affiliation': self.evaluator_affiliation,
            'orcid': self.evaluator_orcid,
            'is_public': self.is_public,
            'ratings': self.ratings,
            'review_text': self.review_text,
            'comments': self.comments
        }


@dataclass
class EvaluationPackageData:
    """Complete data for an evaluation package."""
    paper: PaperMetadata
    evaluations: List[EvaluationData] = field(default_factory=list)
    manager_summary: Optional[str] = None
    evaluation_manager: Optional[str] = None


class PackageAssembler:
    """Assembles evaluation packages from various sources."""

    def __init__(self):
        """Initialize assembler with converters and generators."""
        self.latex_converter = LatexToMarkdownConverter()
        self.template_generator = TemplateGenerator()

    def assemble_from_data(
        self,
        package_data: EvaluationPackageData,
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Assemble complete package from structured data.

        Args:
            package_data: Complete package data
            output_dir: Optional directory to save markdown files

        Returns:
            Dict with 'summary' and 'evaluations' list of markdown strings
        """
        # Process each evaluation's review text
        processed_evaluations = []

        for i, evaluation in enumerate(package_data.evaluations):
            eval_dict = evaluation.to_dict()

            # Convert review text if needed
            if evaluation.review_source_path and evaluation.review_source_type:
                review_text = self._convert_review(
                    evaluation.review_source_path,
                    evaluation.review_source_type
                )
                eval_dict['review_text'] = review_text

            processed_evaluations.append(eval_dict)

        # Generate package
        package = self.template_generator.generate_complete_package(
            paper_info=package_data.paper.to_dict(),
            evaluations=processed_evaluations,
            manager_summary=package_data.manager_summary
        )

        # Save to files if output directory specified
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save summary
            summary_file = output_dir / "evaluation_summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(package['summary'])

            # Save individual evaluations
            for i, eval_md in enumerate(package['evaluations'], 1):
                eval_file = output_dir / f"evaluation_{i}.md"
                with open(eval_file, 'w', encoding='utf-8') as f:
                    f.write(eval_md)

            print(f"Package saved to {output_dir}")

        return package

    def assemble_from_coda(
        self,
        coda_data: Dict,
        paper_metadata: PaperMetadata,
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Assemble package from Coda form data.

        Args:
            coda_data: Data from Coda API
            paper_metadata: Paper information
            output_dir: Optional output directory

        Returns:
            Package dict
        """
        # Parse Coda data into evaluations
        evaluations = []

        for eval_row in coda_data.get('evaluations', []):
            evaluation = EvaluationData(
                ratings=eval_row.get('ratings', {}),
                review_text=eval_row.get('written_evaluation'),
                evaluator_name=eval_row.get('evaluator_name'),
                evaluator_affiliation=eval_row.get('affiliation'),
                evaluator_orcid=eval_row.get('orcid'),
                is_public=eval_row.get('identified', False),
                comments=eval_row.get('additional_comments')
            )
            evaluations.append(evaluation)

        package_data = EvaluationPackageData(
            paper=paper_metadata,
            evaluations=evaluations,
            manager_summary=coda_data.get('manager_summary')
        )

        return self.assemble_from_data(package_data, output_dir)

    def assemble_from_files(
        self,
        paper_metadata: PaperMetadata,
        evaluation_files: List[Dict],
        manager_summary: Optional[str] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Assemble package from local files.

        Args:
            paper_metadata: Paper information
            evaluation_files: List of dicts with:
                - 'ratings': Dict or path to JSON
                - 'review': Path to LaTeX/Word/Markdown file
                - 'evaluator_name': Optional name
                - 'is_public': Whether to show name
            manager_summary: Manager's summary text
            output_dir: Optional output directory

        Returns:
            Package dict
        """
        evaluations = []

        for eval_file_info in evaluation_files:
            # Load ratings
            ratings = eval_file_info['ratings']
            if isinstance(ratings, (str, Path)):
                with open(ratings, 'r') as f:
                    ratings = json.load(f)

            # Determine review source
            review_path = eval_file_info.get('review')
            review_type = None
            if review_path:
                review_path = Path(review_path)
                if review_path.suffix == '.tex':
                    review_type = 'latex'
                elif review_path.suffix in ['.doc', '.docx']:
                    review_type = 'word'
                elif review_path.suffix == '.md':
                    review_type = 'markdown'
                else:
                    review_type = 'text'

            evaluation = EvaluationData(
                ratings=ratings,
                evaluator_name=eval_file_info.get('evaluator_name'),
                evaluator_affiliation=eval_file_info.get('affiliation'),
                evaluator_orcid=eval_file_info.get('orcid'),
                is_public=eval_file_info.get('is_public', False),
                review_source_type=review_type,
                review_source_path=review_path
            )
            evaluations.append(evaluation)

        package_data = EvaluationPackageData(
            paper=paper_metadata,
            evaluations=evaluations,
            manager_summary=manager_summary
        )

        return self.assemble_from_data(package_data, output_dir)

    def _convert_review(self, file_path: Path, file_type: str) -> str:
        """
        Convert review file to markdown.

        Args:
            file_path: Path to review file
            file_type: Type of file ('latex', 'word', 'markdown', 'text')

        Returns:
            Markdown string
        """
        if file_type == 'latex':
            return self.latex_converter.convert_file(file_path)
        elif file_type == 'markdown':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'text':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif file_type == 'word':
            # TODO: Implement Word to markdown conversion
            # For now, require manual conversion or use pandoc
            raise NotImplementedError(
                "Word document conversion not yet implemented. "
                "Please convert to markdown manually or use pandoc."
            )
        else:
            raise ValueError(f"Unknown file type: {file_type}")


def main():
    """Example usage."""
    from pathlib import Path

    # Example: Assemble from local files
    assembler = PackageAssembler()

    paper = PaperMetadata(
        title='Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being',
        authors=['Daniel J. Benjamin', 'Kristen Cooper', 'Ori Heffetz', 'Miles S. Kimball', 'Jiannan Zhou'],
        doi='10.3386/w31728'
    )

    # Example evaluation files
    evaluation_files = [
        {
            'ratings': {
                'overall_assessment': {'lower': 80, 'mid': 95, 'upper': 100},
                'methods': {'lower': 80, 'mid': 90, 'upper': 100},
            },
            'review': '/tmp/review_data/main.tex',
            'evaluator_name': 'Evaluator 1',
            'is_public': False
        }
    ]

    package = assembler.assemble_from_files(
        paper_metadata=paper,
        evaluation_files=evaluation_files,
        manager_summary="This paper makes an important contribution...",
        output_dir=Path('/tmp/evaluation_package')
    )

    print("Package assembled successfully!")
    print(f"Summary length: {len(package['summary'])} chars")
    print(f"Number of evaluations: {len(package['evaluations'])}")


if __name__ == '__main__':
    main()
