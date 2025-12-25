#!/usr/bin/env python3
"""
Template Generator for Unjournal Evaluation Packages

Creates formatted evaluation summary pages following the Unjournal formatting specification.
Uses HTML tables for proper rendering in PubPub.
"""

from typing import Dict, List, Optional
from datetime import datetime


class TemplateGenerator:
    """Generates formatted templates for evaluation packages."""

    # Rating categories in display order
    RATING_CATEGORIES = [
        ('overall_assessment', 'Overall assessment'),
        ('claims_evidence', 'Claims, strength, characterization of evidence'),
        ('advancing_knowledge', 'Advancing knowledge and practice'),
        ('methods', 'Methods: Justification, reasonableness, validity, robustness'),
        ('logic_communication', 'Logic & communication'),
        ('open_collaborative', 'Open, collaborative, replicable'),
        ('real_world_relevance', 'Real-world relevance'),
        ('relevance_to_global_priorities', 'Relevance to global priorities'),
    ]

    # Standard links
    LINKS = {
        'data_presentation': 'https://unjournal.github.io/unjournaldata/chapters/evaluation_data_analysis.html#basic-presentation',
        'evaluator_guidelines': 'https://globalimpact.gitbook.io/the-unjournal-project-and-communication-space/policies-projects-evaluation-workflow/evaluation/guidelines-for-evaluators#metrics-overall-assessment-categories',
        'quantitative_metrics': 'https://globalimpact.gitbook.io/the-unjournal-project-and-communication-space/policies-projects-evaluation-workflow/evaluation/guidelines-for-evaluators#quantitative-metrics',
        'journal_tiers': 'https://globalimpact.gitbook.io/the-unjournal-project-and-communication-space/policies-projects-evaluation-workflow/evaluation/guidelines-for-evaluators#journal-ranking-tiers',
    }

    def _get_rating_value(self, rating_data, key: str = 'mid') -> str:
        """Extract a rating value from various formats."""
        if rating_data is None:
            return ''
        if isinstance(rating_data, (int, float)):
            return str(rating_data)
        if isinstance(rating_data, dict):
            val = rating_data.get(key)
            return str(val) if val is not None else ''
        return str(rating_data)

    def _get_ci_string(self, rating_data) -> str:
        """Get confidence interval string like (80, 90)."""
        if rating_data is None:
            return ''
        if isinstance(rating_data, dict):
            lower = rating_data.get('lower')
            upper = rating_data.get('upper')
            if lower is not None and upper is not None:
                return f"({lower}, {upper})"
        return ''

    def _generate_summary_table(self, evaluations: List[Dict]) -> str:
        """Generate the summary table with overall assessment and journal tier."""
        rows = ['<table>']

        # Header row
        rows.append('  <tr>')
        rows.append('    <th><strong></strong></th>')
        rows.append('    <th><strong>Overall assessment (0-100)</strong></th>')
        rows.append('    <th><strong>Journal rank tier, normative rating (0-5)</strong></th>')
        rows.append('  </tr>')

        # Data rows
        for evaluation in evaluations:
            name = evaluation.get('name', 'Anonymous')
            ratings = evaluation.get('ratings', {})

            overall = self._get_rating_value(ratings.get('overall_assessment'))
            journal_tier = self._get_rating_value(ratings.get('journal_tier_normative'))

            rows.append('  <tr>')
            rows.append(f'    <td><strong>{name}</strong></td>')
            rows.append(f'    <td>{overall}</td>')
            rows.append(f'    <td>{journal_tier}</td>')
            rows.append('  </tr>')

        rows.append('</table>')
        return '\n'.join(rows)

    def _generate_full_ratings_table(self, evaluations: List[Dict]) -> str:
        """Generate the full ratings comparison table.

        Two header rows:
        - Row 1: Empty | Evaluator 1 [Name] | (empty) | (empty) | Evaluator 2 [Name] | ...
        - Row 2: Rating category | Rating (0-100) | 90% CI | Comments | Rating (0-100) | ...
        """
        num_evals = len(evaluations)
        rows = ['<table>']

        # Header row 1: Evaluator names
        rows.append('  <tr>')
        rows.append('    <th></th>')  # Empty cell above "Rating category"
        for i, evaluation in enumerate(evaluations, 1):
            name = evaluation.get('name', 'Anonymous')
            # Format: "Evaluator X [Name]" with Evaluator X bold, name not bold
            if name and name != f'Evaluator {i}' and name != 'Anonymous':
                rows.append(f'    <th><strong>Evaluator {i}</strong> {name}</th>')
            else:
                rows.append(f'    <th><strong>Evaluator {i}</strong> Anonymous</th>')
            rows.append('    <th></th>')  # Empty cell for 90% CI column
            rows.append('    <th></th>')  # Empty cell for Comments column
        rows.append('  </tr>')

        # Header row 2: Column labels
        rows.append('  <tr>')
        rows.append('    <th><strong>Rating category</strong></th>')
        for _ in evaluations:
            rows.append('    <th><strong>Rating (0-100)</strong></th>')
            rows.append('    <th><strong>90% CI</strong></th>')
            rows.append('    <th><strong>Comments</strong></th>')
        rows.append('  </tr>')

        # Data rows for each rating category
        for key, label in self.RATING_CATEGORIES:
            rows.append('  <tr>')
            rows.append(f'    <td><strong>{label}</strong></td>')

            for evaluation in evaluations:
                ratings = evaluation.get('ratings', {})
                rating_data = ratings.get(key)

                mid_val = self._get_rating_value(rating_data)
                ci_str = self._get_ci_string(rating_data)
                comment = ''  # Comments can be added to evaluation data if needed

                rows.append(f'    <td>{mid_val}</td>')
                rows.append(f'    <td>{ci_str}</td>')
                rows.append(f'    <td>{comment}</td>')

            rows.append('  </tr>')

        rows.append('</table>')
        return '\n'.join(rows)

    def _generate_journal_tier_table(self, evaluations: List[Dict]) -> str:
        """Generate the journal ranking tiers table.

        Two header rows:
        - Row 1: Empty | Evaluator 1 [Name] | (empty) | (empty) | Evaluator 2 [Name] | ...
        - Row 2: Judgment | Ranking tier (0-5) | 90% CI | Comments | Ranking tier (0-5) | ...
        """
        num_evals = len(evaluations)
        total_cols = 1 + (num_evals * 3)  # First col + 3 cols per evaluator (tier, CI, comments)

        rows = ['<table>']

        # Header row 1: Evaluator names
        rows.append('  <tr>')
        rows.append('    <th></th>')  # Empty cell above "Judgment"
        for i, evaluation in enumerate(evaluations, 1):
            name = evaluation.get('name', 'Anonymous')
            # Format: "Evaluator X [Name]" with Evaluator X bold, name not bold
            if name and name != f'Evaluator {i}' and name != 'Anonymous':
                rows.append(f'    <th><strong>Evaluator {i}</strong> {name}</th>')
            else:
                rows.append(f'    <th><strong>Evaluator {i}</strong> Anonymous</th>')
            rows.append('    <th></th>')  # Empty cell for 90% CI column
            rows.append('    <th></th>')  # Empty cell for Comments column
        rows.append('  </tr>')

        # Header row 2: Column labels
        rows.append('  <tr>')
        rows.append('    <th><strong>Judgment</strong></th>')
        for _ in evaluations:
            rows.append('    <th><strong>Ranking tier (0-5)</strong></th>')
            rows.append('    <th><strong>90% CI</strong></th>')
            rows.append('    <th><strong>Comments</strong></th>')
        rows.append('  </tr>')

        # Row 1: Normative (should)
        rows.append('  <tr>')
        rows.append("    <td>On a 'scale of journals', what 'quality of journal' <em>should</em> this be published in?</td>")
        for evaluation in evaluations:
            ratings = evaluation.get('ratings', {})
            rating_data = ratings.get('journal_tier_normative')
            mid_val = self._get_rating_value(rating_data)
            ci_str = self._get_ci_string(rating_data)
            comment = evaluation.get('comments', {}).get('journal', '') if isinstance(evaluation.get('comments'), dict) else ''
            rows.append(f'    <td>{mid_val}</td>')
            rows.append(f'    <td>{ci_str}</td>')
            rows.append(f'    <td>{comment}</td>')
        rows.append('  </tr>')

        # Row 2: Predictive (will)
        rows.append('  <tr>')
        rows.append("    <td>What 'quality journal' do you expect this work <em>will</em> be published in?</td>")
        for evaluation in evaluations:
            ratings = evaluation.get('ratings', {})
            rating_data = ratings.get('journal_tier_predictive')
            mid_val = self._get_rating_value(rating_data)
            ci_str = self._get_ci_string(rating_data)
            rows.append(f'    <td>{mid_val}</td>')
            rows.append(f'    <td>{ci_str}</td>')
            rows.append(f'    <td></td>')  # Empty comment for predictive row
        rows.append('  </tr>')

        # Explanation row - 2 cells only (link in left, tier descriptions in right)
        rows.append('  <tr>')
        rows.append(f'    <td><a href="{self.LINKS["journal_tiers"]}">See here</a> for more details on these tiers.</td>')
        rows.append('    <td><em>We summarize these as:</em><br/>• 0.0: Marginally respectable/Little to no value<br/>• 1.0: OK/Somewhat valuable<br/>• 2.0: Marginal B-journal/Decent field journal<br/>• 3.0: Top B-journal/Strong field journal<br/>• 4.0: Marginal A-Journal/Top field journal<br/>• 5.0: A-journal/Top journal</td>')
        rows.append('  </tr>')

        rows.append('</table>')
        return '\n'.join(rows)

    def _generate_claims_table(self, evaluations: List[Dict]) -> str:
        """Generate the claims identification and assessment table."""
        rows = ['<table>']

        # Header row
        rows.append('  <tr>')
        rows.append('    <th></th>')
        rows.append('    <th><strong>Main research claim</strong></th>')
        rows.append('    <th><strong>Belief in claim</strong></th>')
        rows.append('    <th><strong>Suggested robustness checks</strong></th>')
        rows.append("    <th><strong>Important 'implication', policy, credibility</strong></th>")
        rows.append('  </tr>')

        # Data rows for each evaluator
        for i, evaluation in enumerate(evaluations, 1):
            name = evaluation.get('name', 'Anonymous')

            main_claim = evaluation.get('main_research_claim', '')
            belief = evaluation.get('belief_in_claim', '')
            robustness = evaluation.get('suggested_robustness_checks', '')
            implication = evaluation.get('important_implication', '')

            rows.append('  <tr>')
            rows.append(f'    <td><strong>Evaluator {i}</strong><br/>{name}</td>')
            rows.append(f'    <td>{main_claim}</td>')
            rows.append(f'    <td>{belief}</td>')
            rows.append(f'    <td>{robustness}</td>')
            rows.append(f'    <td>{implication}</td>')
            rows.append('  </tr>')

        rows.append('</table>')
        return '\n'.join(rows)

    def generate_evaluation_summary(
        self,
        paper_info: Dict,
        evaluations: List[Dict],
        manager_summary: Optional[str] = None,
        evaluation_links: Optional[List[str]] = None
    ) -> str:
        """
        Generate evaluation summary page following the Unjournal formatting spec.

        Args:
            paper_info: Dict with paper metadata (title, authors, doi, url)
            evaluations: List of evaluation dicts with ratings, summary, claims data
            manager_summary: Optional manager's discussion text
            evaluation_links: Optional list of links to individual evaluation pages

        Returns:
            Formatted content for evaluation summary page
        """
        sections = []
        title = paper_info.get('title', 'Untitled Paper')
        num_evals = len(evaluations)
        plural = 's' if num_evals != 1 else ''

        # ============================================================
        # Section 1: Abstract
        # ============================================================
        sections.append('# Abstract\n')
        sections.append(f'We organized {num_evals} evaluation{plural} of the paper: "{title}". To read these evaluations, please see the links below.\n')

        # ============================================================
        # Section 2: Evaluations List
        # ============================================================
        sections.append('\n## **Evaluations**\n')
        for i, evaluation in enumerate(evaluations, 1):
            name = evaluation.get('name', f'Evaluator {i}')
            if evaluation_links and i <= len(evaluation_links):
                link = evaluation_links[i - 1]
                sections.append(f'{i}. [{name}]({link})\n')
            else:
                sections.append(f'{i}. {name} *[Link to be added]*\n')

        # ============================================================
        # Section 3: Overall Ratings
        # ============================================================
        sections.append('\n# **Overall ratings**\n')
        sections.append('We asked evaluators to provide overall assessments as well as ratings for a range of specific criteria.\n')
        sections.append('\n**I. Overall assessment** (See footnote)\n')
        sections.append("\n**II. Journal rank tier, normative rating (0-5):** On a 'scale of journals', what 'quality of journal' *should* this be published in? Note: 0 = lowest/none, 5 = highest/best.\n")

        # Summary table
        sections.append('\n' + self._generate_summary_table(evaluations) + '\n')

        sections.append(f'\nSee "[Metrics](#metrics)" below for a more detailed breakdown of the evaluators\' ratings across several categories. To see these ratings in the context of all Unjournal ratings, with some analysis, see our [data presentation here]({self.LINKS["data_presentation"]}).\n')
        sections.append(f'\n[See here]({self.LINKS["evaluator_guidelines"]}) for the current full evaluator guidelines, including further explanation of the requested ratings.\n')

        # ============================================================
        # Section 4: Evaluation Summaries
        # ============================================================
        sections.append('\n## **Evaluation Summaries**\n')
        for evaluation in evaluations:
            name = evaluation.get('name', 'Anonymous')
            summary = evaluation.get('summary', '*[Summary to be added]*')
            sections.append(f'\n## {name}\n')
            sections.append(f'\n{summary}\n')

        # ============================================================
        # Section 5: Metrics - Ratings
        # ============================================================
        sections.append('\n# **Metrics**\n')
        sections.append('\n## Ratings\n')
        sections.append(f'\n[See here]({self.LINKS["quantitative_metrics"]}) for details on the categories below, and the guidance given to evaluators.\n')
        sections.append('\n' + self._generate_full_ratings_table(evaluations) + '\n')

        # ============================================================
        # Section 6: Journal Ranking Tiers
        # ============================================================
        sections.append('\n## Journal ranking tiers\n')
        sections.append(f'\n[See here]({self.LINKS["journal_tiers"]}) for more details on these tiers.\n')
        sections.append('\n' + self._generate_journal_tier_table(evaluations) + '\n')

        # ============================================================
        # Section 7: Claim Identification and Assessment
        # ============================================================
        sections.append('\n# **Claim identification and assessment (summary)**\n')
        sections.append('\n*For the full discussions, see the corresponding sections in each linked evaluation.*\n')
        sections.append('\n' + self._generate_claims_table(evaluations) + '\n')

        # ============================================================
        # Section 8: References
        # ============================================================
        sections.append('\n## References\n')
        sections.append('\n1. ' + self._format_reference_markdown(paper_info) + '\n')

        # ============================================================
        # Section 9: Evaluation Manager's Discussion
        # ============================================================
        sections.append("\n# **Evaluation manager's discussion**\n")
        if manager_summary:
            sections.append(f'\n{manager_summary}\n')
        else:
            sections.append("\n*[Manager's discussion to be added]*\n")

        # ============================================================
        # Section 10-11: Unjournal Process Notes
        # ============================================================
        sections.append('\n# Unjournal process notes\n')
        sections.append('\n## Why we chose this paper\n')
        sections.append('\n*[To be added]*\n')
        sections.append('\n## Evaluation process\n')
        sections.append('\n*[To be added]*\n')
        sections.append('\n### COI issues\n')
        sections.append('\n*[To be added]*\n')

        return ''.join(sections)

    def generate_individual_evaluation(
        self,
        paper_info: Dict,
        evaluation_data: Dict,
        evaluation_number: int = 1
    ) -> str:
        """
        Generate individual evaluation document.

        Args:
            paper_info: Dict with paper metadata
            evaluation_data: Dict with evaluation data (ratings, review text, evaluator info)
            evaluation_number: The evaluation number (1, 2, etc.)

        Returns:
            Formatted content for individual evaluation
        """
        sections = []
        paper_title = paper_info.get('title', 'Untitled Paper')
        evaluator_name = evaluation_data.get('name', 'Anonymous')

        # Title
        sections.append(f'# Evaluation {evaluation_number} of "{paper_title}"\n')
        sections.append(f'\n**Evaluator:** {evaluator_name}\n')

        # Evaluator info
        if evaluation_data.get('affiliation'):
            sections.append(f"**Affiliation:** {evaluation_data['affiliation']}\n")
        if evaluation_data.get('orcid'):
            sections.append(f"**ORCID:** [{evaluation_data['orcid']}](https://orcid.org/{evaluation_data['orcid']})\n")

        # Summary
        if evaluation_data.get('summary'):
            sections.append('\n## Summary\n')
            sections.append(f"\n{evaluation_data['summary']}\n")

        # Full review text
        if evaluation_data.get('review_text'):
            sections.append('\n## Detailed Review\n')
            sections.append(f"\n{evaluation_data['review_text']}\n")

        # Ratings table (simplified for individual page)
        if evaluation_data.get('ratings'):
            sections.append('\n## Ratings\n')
            sections.append('\n<table>\n')
            sections.append('  <tr>\n')
            sections.append('    <th><strong>Category</strong></th>\n')
            sections.append('    <th><strong>Rating</strong></th>\n')
            sections.append('    <th><strong>90% CI</strong></th>\n')
            sections.append('  </tr>\n')

            ratings = evaluation_data['ratings']
            for key, label in self.RATING_CATEGORIES:
                if key in ratings:
                    rating_data = ratings[key]
                    mid_val = self._get_rating_value(rating_data)
                    ci_str = self._get_ci_string(rating_data)
                    sections.append('  <tr>\n')
                    sections.append(f'    <td><strong>{label}</strong></td>\n')
                    sections.append(f'    <td>{mid_val}</td>\n')
                    sections.append(f'    <td>{ci_str}</td>\n')
                    sections.append('  </tr>\n')

            # Journal tiers
            for key, label in [('journal_tier_normative', 'Journal tier (normative)'),
                               ('journal_tier_predictive', 'Journal tier (predictive)')]:
                if key in ratings:
                    rating_data = ratings[key]
                    mid_val = self._get_rating_value(rating_data)
                    ci_str = self._get_ci_string(rating_data)
                    sections.append('  <tr>\n')
                    sections.append(f'    <td><strong>{label}</strong></td>\n')
                    sections.append(f'    <td>{mid_val}</td>\n')
                    sections.append(f'    <td>{ci_str}</td>\n')
                    sections.append('  </tr>\n')

            sections.append('</table>\n')

        # Claims assessment
        has_claims = any(evaluation_data.get(k) for k in ['main_research_claim', 'belief_in_claim',
                                                           'suggested_robustness_checks', 'important_implication'])
        if has_claims:
            sections.append('\n## Claim Assessment\n')
            if evaluation_data.get('main_research_claim'):
                sections.append(f"\n**Main research claim:** {evaluation_data['main_research_claim']}\n")
            if evaluation_data.get('belief_in_claim'):
                sections.append(f"\n**Belief in claim:** {evaluation_data['belief_in_claim']}\n")
            if evaluation_data.get('suggested_robustness_checks'):
                sections.append(f"\n**Suggested robustness checks:** {evaluation_data['suggested_robustness_checks']}\n")
            if evaluation_data.get('important_implication'):
                sections.append(f"\n**Important implication:** {evaluation_data['important_implication']}\n")

        # References (for Scholar-friendly parsing)
        sections.append('\n## References\n')
        sections.append('\n1. ' + self._format_reference_markdown(paper_info) + '\n')

        return ''.join(sections)

    @staticmethod
    def _format_reference_markdown(paper_info: Dict) -> str:
        """Build a single reference line for the reviewed paper."""
        title = paper_info.get('title', 'Untitled Paper')
        authors = paper_info.get('authors') or []
        if isinstance(authors, str):
            authors = [authors]
        authors_str = ', '.join(a for a in authors if a) or 'Unknown author'
        year = paper_info.get('year')
        year_str = f" ({year})" if year else ""
        doi = paper_info.get('doi')
        url = paper_info.get('url')
        doi_url = None
        if doi:
            doi_url = doi if doi.startswith('http') else f"https://doi.org/{doi}"
        link = doi_url or url
        link_str = f" {link}" if link else ""
        return f"{authors_str}{year_str}. {title}.{link_str}"

    def generate_complete_package(
        self,
        paper_info: Dict,
        evaluations: List[Dict],
        manager_summary: Optional[str] = None,
        evaluation_links: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate complete evaluation package (summary + all individual evaluations).

        Args:
            paper_info: Paper metadata
            evaluations: List of evaluation data
            manager_summary: Optional manager summary
            evaluation_links: Optional list of links to evaluation pages

        Returns:
            Dict with 'summary' and 'evaluations' keys
        """
        package = {}

        # Generate summary
        package['summary'] = self.generate_evaluation_summary(
            paper_info,
            evaluations,
            manager_summary,
            evaluation_links
        )

        # Generate individual evaluations
        package['evaluations'] = []
        for i, evaluation in enumerate(evaluations, 1):
            eval_content = self.generate_individual_evaluation(
                paper_info,
                evaluation,
                evaluation_number=i
            )
            package['evaluations'].append(eval_content)

        return package


def main():
    """Example usage with sample data."""

    # Example paper info
    paper_info = {
        'title': 'Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being',
        'authors': ['Daniel J. Benjamin', 'Kristen Cooper', 'Ori Heffetz'],
        'doi': '10.3386/w31728',
    }

    # Example evaluations matching the expected data structure
    evaluations = [
        {
            'name': 'Alberto Prati',
            'ratings': {
                'overall_assessment': {'lower': 90, 'mid': 95, 'upper': 100},
                'claims_evidence': {'lower': 90, 'mid': 95, 'upper': 100},
                'advancing_knowledge': {'lower': 90, 'mid': 95, 'upper': 100},
                'methods': {'lower': 90, 'mid': 95, 'upper': 100},
                'logic_communication': {'lower': 89, 'mid': 95, 'upper': 100},
                'open_collaborative': {'lower': 90, 'mid': 95, 'upper': 100},
                'relevance_to_global_priorities': {'lower': 74, 'mid': 86, 'upper': 95},
                'journal_tier_normative': {'lower': 5, 'mid': 5, 'upper': 5},
                'journal_tier_predictive': {'lower': 4.5, 'mid': 4.8, 'upper': 5},
            },
            'summary': 'This is an excellent paper that makes important methodological contributions to the measurement of well-being.',
            'main_research_claim': 'Scale-use heterogeneity significantly biases well-being comparisons.',
            'belief_in_claim': 'High confidence based on robust methodology.',
            'suggested_robustness_checks': 'Additional cross-cultural validation.',
            'important_implication': 'Policy implications for well-being measurement.',
        },
        {
            'name': 'Caspar Kaiser',
            'ratings': {
                'overall_assessment': {'lower': 80, 'mid': 95, 'upper': 100},
                'claims_evidence': {'lower': 70, 'mid': 80, 'upper': 90},
                'advancing_knowledge': {'lower': 80, 'mid': 90, 'upper': 100},
                'methods': {'lower': 80, 'mid': 90, 'upper': 100},
                'logic_communication': {'lower': 60, 'mid': 75, 'upper': 90},
                'open_collaborative': {'lower': 70, 'mid': 85, 'upper': 90},
                'relevance_to_global_priorities': {'lower': 0, 'mid': 0, 'upper': 0},
                'journal_tier_normative': {'lower': 4.7, 'mid': 4.1, 'upper': 5},
                'journal_tier_predictive': {'lower': 4.4, 'mid': 4, 'upper': 5},
            },
            'summary': 'A solid contribution with some areas for improvement in presentation.',
            'main_research_claim': 'The proposed adjustment method improves comparability.',
            'belief_in_claim': 'Moderate confidence.',
            'suggested_robustness_checks': 'Test with different populations.',
            'important_implication': 'Useful for international comparisons.',
        },
    ]

    # Generate package
    generator = TemplateGenerator()
    package = generator.generate_complete_package(
        paper_info,
        evaluations,
        manager_summary="This paper represents an important methodological advance in well-being research."
    )

    print("=== EVALUATION SUMMARY ===\n")
    print(package['summary'])
    print("\n\n=== INDIVIDUAL EVALUATION 1 ===\n")
    print(package['evaluations'][0])


if __name__ == '__main__':
    main()
