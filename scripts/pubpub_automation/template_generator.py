#!/usr/bin/env python3
"""
Template Generator for Unjournal Evaluation Packages

Creates markdown templates for evaluation summaries and individual evaluations.
Templates are filled with paper metadata and evaluation data.
"""

from typing import Dict, List, Optional
from datetime import datetime


class TemplateGenerator:
    """Generates markdown templates for evaluation packages."""

    def generate_evaluation_summary(
        self,
        paper_info: Dict,
        evaluations: List[Dict],
        manager_summary: Optional[str] = None,
        include_comparison_table: bool = True
    ) -> str:
        """
        Generate evaluation summary document.

        Args:
            paper_info: Dict with paper metadata (title, authors, doi, url, etc.)
            evaluations: List of evaluation dicts (each with ratings, evaluator name if public)
            manager_summary: Optional manager's summary text
            include_comparison_table: Include comparison table of all ratings

        Returns:
            Markdown content for evaluation summary
        """
        sections = []

        # Title
        title = paper_info.get('title', 'Untitled Paper')
        sections.append(f"# Evaluation Summary: {title}\n")

        # Paper metadata
        sections.append("## Paper Information\n")

        if paper_info.get('authors'):
            authors_list = paper_info['authors']
            if isinstance(authors_list, list):
                authors_str = ", ".join(authors_list)
            else:
                authors_str = str(authors_list)
            sections.append(f"**Authors:** {authors_str}\n")

        if paper_info.get('doi'):
            sections.append(f"**DOI:** [{paper_info['doi']}](https://doi.org/{paper_info['doi']})\n")
        elif paper_info.get('url'):
            sections.append(f"**URL:** {paper_info['url']}\n")

        if paper_info.get('abstract'):
            sections.append(f"\n**Abstract:** {paper_info['abstract']}\n")

        # Evaluation overview
        sections.append(f"\n## Evaluation Overview\n")
        sections.append(f"This paper was evaluated by **{len(evaluations)} reviewer(s)**.\n")
        sections.append(f"*Evaluation date: {datetime.now().strftime('%B %Y')}*\n")

        # Manager's summary
        if manager_summary:
            sections.append("\n## Evaluation Manager's Summary\n")
            sections.append(manager_summary + "\n")
        else:
            sections.append("\n## Evaluation Manager's Summary\n")
            sections.append("*[To be added by evaluation manager]*\n")

        # Ratings comparison table
        if include_comparison_table and evaluations:
            try:
                from .ratings_table_generator import RatingsTableGenerator
            except ImportError:
                from ratings_table_generator import RatingsTableGenerator

            # Build comparison data
            evaluators_ratings = {}
            for i, evaluation in enumerate(evaluations):
                # Use evaluator name if public, otherwise anonymous
                if evaluation.get('name') and evaluation.get('is_public', False):
                    eval_name = evaluation['name']
                else:
                    eval_name = f"Evaluator {i+1}"

                if 'ratings' in evaluation:
                    evaluators_ratings[eval_name] = evaluation['ratings']

            if evaluators_ratings:
                generator = RatingsTableGenerator()
                comparison_table = generator.generate_comparison_table(evaluators_ratings)
                sections.append(f"\n{comparison_table}\n")

        # Key findings section (placeholder)
        sections.append("\n## Key Findings\n")
        sections.append("*[Key findings from the evaluations will be summarized here]*\n")

        # Strengths and weaknesses
        sections.append("\n## Strengths\n")
        sections.append("*[Common strengths identified across evaluations]*\n")

        sections.append("\n## Areas for Improvement\n")
        sections.append("*[Common suggestions for improvement]*\n")

        # Links to individual evaluations
        sections.append("\n## Individual Evaluations\n")
        sections.append("See the linked individual evaluation reports for detailed feedback:\n")
        for i, evaluation in enumerate(evaluations):
            if evaluation.get('name') and evaluation.get('is_public', False):
                eval_label = f"Evaluation by {evaluation['name']}"
            else:
                eval_label = f"Evaluation {i+1}"
            sections.append(f"- {eval_label} *[Link will be added automatically]*\n")

        return '\n'.join(sections)

    def generate_individual_evaluation(
        self,
        paper_info: Dict,
        evaluation_data: Dict,
        include_written_review: bool = True,
        include_ratings: bool = True
    ) -> str:
        """
        Generate individual evaluation document.

        Args:
            paper_info: Dict with paper metadata
            evaluation_data: Dict with evaluation data (ratings, review text, evaluator info)
            include_written_review: Include the written review section
            include_ratings: Include ratings table

        Returns:
            Markdown content for individual evaluation
        """
        sections = []

        # Title
        paper_title = paper_info.get('title', 'Untitled Paper')
        evaluator_name = evaluation_data.get('name', 'Anonymous')

        if evaluation_data.get('is_public', False):
            sections.append(f"# Evaluation of \"{paper_title}\" by {evaluator_name}\n")
        else:
            sections.append(f"# Evaluation of \"{paper_title}\"\n")

        # Evaluator info (if public)
        if evaluation_data.get('is_public', False):
            sections.append("## Evaluator\n")
            if evaluation_data.get('name'):
                sections.append(f"**Name:** {evaluation_data['name']}\n")
            if evaluation_data.get('affiliation'):
                sections.append(f"**Affiliation:** {evaluation_data['affiliation']}\n")
            if evaluation_data.get('orcid'):
                sections.append(f"**ORCID:** [{evaluation_data['orcid']}](https://orcid.org/{evaluation_data['orcid']})\n")

        # Ratings table
        if include_ratings and evaluation_data.get('ratings'):
            try:
                from .ratings_table_generator import generate_full_evaluation_ratings
            except ImportError:
                from ratings_table_generator import generate_full_evaluation_ratings

            ratings_markdown = generate_full_evaluation_ratings(
                evaluation_data,
                include_summary=True,
                include_descriptions=False
            )
            sections.append(f"\n{ratings_markdown}\n")

        # Written review
        if include_written_review:
            sections.append("\n## Detailed Review\n")
            if evaluation_data.get('review_text'):
                sections.append(evaluation_data['review_text'] + "\n")
            else:
                sections.append("*[Written review will be added here]*\n")

        # Additional comments
        if evaluation_data.get('comments'):
            sections.append("\n## Additional Comments\n")
            sections.append(evaluation_data['comments'] + "\n")

        return '\n'.join(sections)

    def generate_complete_package(
        self,
        paper_info: Dict,
        evaluations: List[Dict],
        manager_summary: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate complete evaluation package (summary + all individual evaluations).

        Args:
            paper_info: Paper metadata
            evaluations: List of evaluation data
            manager_summary: Optional manager summary

        Returns:
            Dict with 'summary' and 'evaluations' keys containing markdown strings
        """
        package = {}

        # Generate summary
        package['summary'] = self.generate_evaluation_summary(
            paper_info,
            evaluations,
            manager_summary,
            include_comparison_table=True
        )

        # Generate individual evaluations
        package['evaluations'] = []
        for evaluation in evaluations:
            eval_markdown = self.generate_individual_evaluation(
                paper_info,
                evaluation,
                include_written_review=True,
                include_ratings=True
            )
            package['evaluations'].append(eval_markdown)

        return package


def main():
    """Example usage."""
    import json

    # Example paper info
    paper_info = {
        'title': 'Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being',
        'authors': ['Daniel J. Benjamin', 'Kristen Cooper', 'Ori Heffetz', 'Miles S. Kimball', 'Jiannan Zhou'],
        'doi': '10.3386/w31728',
        'abstract': 'This paper addresses scale-use heterogeneity in self-reported well-being...'
    }

    # Example evaluations
    evaluations = [
        {
            'name': 'Evaluator 1',
            'is_public': False,  # Anonymous for now
            'ratings': {
                'overall_assessment': {'lower': 80, 'mid': 95, 'upper': 100},
                'methods': {'lower': 80, 'mid': 90, 'upper': 100},
            },
            'review_text': 'This is an excellent paper...'
        },
        {
            'name': 'Evaluator 2',
            'is_public': False,
            'ratings': {
                'overall_assessment': {'lower': 90, 'mid': 95, 'upper': 100},
                'methods': 88,
            }
        }
    ]

    # Generate package
    generator = TemplateGenerator()
    package = generator.generate_complete_package(
        paper_info,
        evaluations,
        manager_summary="This paper makes an important methodological contribution..."
    )

    print("=== EVALUATION SUMMARY ===\n")
    print(package['summary'])
    print("\n\n=== INDIVIDUAL EVALUATION 1 ===\n")
    print(package['evaluations'][0])


if __name__ == '__main__':
    main()
