#!/usr/bin/env python3
"""
Ratings Table Generator for Unjournal Evaluations

Generates markdown tables from evaluation ratings data.
Supports both numeric ranges and categorical ratings.
Works with any evaluation data structure from Coda.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class RatingValue:
    """A single rating value with optional range."""
    lower: Optional[float] = None
    mid: Optional[float] = None
    upper: Optional[float] = None

    def __str__(self) -> str:
        """Format rating as string."""
        if self.mid is not None:
            if self.lower is not None and self.upper is not None:
                return f"{self.mid} ({self.lower}-{self.upper})"
            else:
                return f"{self.mid}"
        elif self.lower is not None and self.upper is not None:
            return f"{self.lower}-{self.upper}"
        elif self.lower is not None:
            return f"{self.lower}+"
        else:
            return "Not provided"

    @classmethod
    def from_dict(cls, data: Union[Dict, float, int, str]) -> 'RatingValue':
        """Create RatingValue from dict, number, or string."""
        if isinstance(data, (int, float)):
            return cls(mid=float(data))
        elif isinstance(data, dict):
            return cls(
                lower=data.get('lower'),
                mid=data.get('mid'),
                upper=data.get('upper')
            )
        elif isinstance(data, str):
            # Try to parse string like "95 (90-100)" or "90-100"
            try:
                if '(' in data and ')' in data:
                    # Format: "95 (90-100)"
                    parts = data.split('(')
                    mid = float(parts[0].strip())
                    range_part = parts[1].replace(')', '').strip()
                    lower, upper = map(float, range_part.split('-'))
                    return cls(lower=lower, mid=mid, upper=upper)
                elif '-' in data:
                    # Format: "90-100"
                    lower, upper = map(float, data.split('-'))
                    return cls(lower=lower, upper=upper, mid=(lower+upper)/2)
                else:
                    # Single number
                    return cls(mid=float(data))
            except:
                return cls()
        else:
            return cls()


class RatingsTableGenerator:
    """Generates markdown tables for evaluation ratings."""

    # Standard Unjournal criteria with descriptions
    STANDARD_CRITERIA = {
        'overall_assessment': {
            'label': 'Overall Assessment',
            'description': 'Overall assessment of the research quality',
            'scale': '0-100',
        },
        'advancing_knowledge': {
            'label': 'Advancing Knowledge & Practice',
            'description': 'How much does this work advance our knowledge and practice?',
            'scale': '0-100',
        },
        'methods': {
            'label': 'Methods: Justification & Reasonableness',
            'description': 'Justification and reasonableness of methods, robustness',
            'scale': '0-100',
        },
        'logic_communication': {
            'label': 'Logic & Communication',
            'description': 'Logic, reasoning, and communication of arguments',
            'scale': '0-100',
        },
        'open_collaborative': {
            'label': 'Open, Collaborative, Replicable',
            'description': 'Openness, collaborative approach, and replicability',
            'scale': '0-100',
        },
        'real_world_relevance': {
            'label': 'Real-World Relevance',
            'description': 'Relevance to real-world issues and global priorities',
            'scale': '0-100',
        },
        'relevance_to_global_priorities': {
            'label': 'Relevance to Global Priorities',
            'description': 'Specific relevance to global priorities research',
            'scale': '0-100',
        },
        'journal_merit': {
            'label': 'Journal Tier (Prediction)',
            'description': 'Predicted tier of journal it could be published in',
            'scale': '0-5 (journal tier)',
        },
        'claims_evidence': {
            'label': 'Claims Supported by Evidence',
            'description': 'Are the paper\'s claims credibly supported by evidence?',
            'scale': '0-100',
        },
    }

    def generate_ratings_table(
        self,
        ratings: Dict[str, Union[Dict, float, int, str]],
        evaluator_name: Optional[str] = None,
        include_descriptions: bool = False
    ) -> str:
        """
        Generate markdown table from ratings data.

        Args:
            ratings: Dict mapping criterion to rating value
            evaluator_name: Name of evaluator (for header)
            include_descriptions: Include description column

        Returns:
            Markdown table string
        """
        lines = []

        # Header
        if evaluator_name:
            lines.append(f"### Ratings by {evaluator_name}\n")
        else:
            lines.append("### Evaluation Ratings\n")

        # Table header
        if include_descriptions:
            lines.append("| Criterion | Rating | Scale | Description |")
            lines.append("|-----------|--------|-------|-------------|")
        else:
            lines.append("| Criterion | Rating | Scale |")
            lines.append("|-----------|--------|-------|")

        # Table rows
        for criterion_key, rating_data in ratings.items():
            # Get criterion info
            if criterion_key in self.STANDARD_CRITERIA:
                criterion_info = self.STANDARD_CRITERIA[criterion_key]
                label = criterion_info['label']
                scale = criterion_info['scale']
                description = criterion_info.get('description', '')
            else:
                # Custom criterion - auto-generate nice label
                label = criterion_key.replace('_', ' ').title()
                scale = 'Custom'
                description = ''

            # Format rating value
            rating = RatingValue.from_dict(rating_data)

            # Build row
            if include_descriptions:
                lines.append(f"| {label} | {rating} | {scale} | {description} |")
            else:
                lines.append(f"| {label} | {rating} | {scale} |")

        return '\n'.join(lines)

    def generate_comparison_table(
        self,
        evaluators_ratings: Dict[str, Dict[str, Union[Dict, float, int]]],
        criteria_subset: Optional[List[str]] = None
    ) -> str:
        """
        Generate comparison table for multiple evaluators.

        Args:
            evaluators_ratings: Dict mapping evaluator name to their ratings
            criteria_subset: Optional list of criteria to include (None = all)

        Returns:
            Markdown comparison table
        """
        lines = []
        lines.append("### Ratings Comparison\n")

        # Determine criteria to include
        if criteria_subset:
            criteria = criteria_subset
        else:
            # Collect all criteria from all evaluators
            all_criteria = set()
            for ratings in evaluators_ratings.values():
                all_criteria.update(ratings.keys())
            criteria = sorted(all_criteria)

        # Build header
        evaluator_names = list(evaluators_ratings.keys())
        header = "| Criterion | " + " | ".join(evaluator_names) + " |"
        separator = "|-----------|" + "|".join(["--------"] * len(evaluator_names)) + "|"
        lines.append(header)
        lines.append(separator)

        # Build rows
        for criterion_key in criteria:
            # Get criterion label
            if criterion_key in self.STANDARD_CRITERIA:
                label = self.STANDARD_CRITERIA[criterion_key]['label']
            else:
                label = criterion_key.replace('_', ' ').title()

            # Get ratings from each evaluator
            ratings_row = [label]
            for evaluator_name in evaluator_names:
                evaluator_ratings = evaluators_ratings[evaluator_name]
                if criterion_key in evaluator_ratings:
                    rating = RatingValue.from_dict(evaluator_ratings[criterion_key])
                    ratings_row.append(str(rating))
                else:
                    ratings_row.append("—")

            lines.append("| " + " | ".join(ratings_row) + " |")

        return '\n'.join(lines)

    def generate_summary_stats(
        self,
        ratings: Dict[str, Union[Dict, float, int]]
    ) -> str:
        """
        Generate summary statistics from ratings.

        Args:
            ratings: Rating values

        Returns:
            Markdown summary
        """
        lines = []
        lines.append("### Rating Summary\n")

        # Calculate average (using mid values)
        mid_values = []
        for rating_data in ratings.values():
            rating = RatingValue.from_dict(rating_data)
            if rating.mid is not None:
                mid_values.append(rating.mid)

        if mid_values:
            avg = sum(mid_values) / len(mid_values)
            lines.append(f"- **Average Rating:** {avg:.1f}/100")
            lines.append(f"- **Highest Rating:** {max(mid_values):.1f}")
            lines.append(f"- **Lowest Rating:** {min(mid_values):.1f}")
            lines.append(f"- **Number of Criteria:** {len(mid_values)}")

        return '\n'.join(lines)


def generate_full_evaluation_ratings(
    evaluator_data: Dict,
    include_summary: bool = True,
    include_descriptions: bool = False
) -> str:
    """
    Generate complete ratings section for an evaluation.

    Args:
        evaluator_data: Dict with 'name' and 'ratings' keys
        include_summary: Include summary statistics
        include_descriptions: Include descriptions in table

    Returns:
        Complete markdown ratings section
    """
    generator = RatingsTableGenerator()

    sections = []

    # Main ratings table
    ratings_table = generator.generate_ratings_table(
        evaluator_data['ratings'],
        evaluator_name=evaluator_data.get('name'),
        include_descriptions=include_descriptions
    )
    sections.append(ratings_table)

    # Summary statistics
    if include_summary:
        summary = generator.generate_summary_stats(evaluator_data['ratings'])
        sections.append('\n' + summary)

    return '\n\n'.join(sections)


def main():
    """Example usage with sample data."""
    import json

    # Example: ratings from any evaluator
    example_ratings = {
        'overall_assessment': {'lower': 80, 'mid': 95, 'upper': 100},
        'advancing_knowledge': 92,  # Can be just a number
        'methods': '85 (80-90)',  # Or a string
    }

    evaluator_data = {
        'name': 'Example Evaluator',
        'ratings': example_ratings
    }

    # Generate table
    markdown = generate_full_evaluation_ratings(
        evaluator_data,
        include_summary=True,
        include_descriptions=False
    )

    print(markdown)
    print("\n" + "="*50 + "\n")

    # Example: comparison of multiple evaluators
    generator = RatingsTableGenerator()
    comparison = generator.generate_comparison_table({
        'Evaluator 1': {'overall_assessment': 95, 'methods': 90},
        'Evaluator 2': {'overall_assessment': 85, 'methods': 88},
    })
    print(comparison)


if __name__ == '__main__':
    main()
