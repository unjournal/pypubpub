#!/usr/bin/env python3
"""
Fetch evaluation ratings from Coda for PubPub ratings table generation.

This script fetches evaluation ratings from the Coda academic stream evaluations
table and formats them for use with the RatingsTableGenerator.

Usage:
    from scripts.coda_integration.fetch_ratings import CodaRatingsFetcher

    fetcher = CodaRatingsFetcher()
    ratings = fetcher.get_ratings_for_paper("Paper Title")
    # Returns dict ready for RatingsTableGenerator
"""

import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()


class CodaRatingsFetcher:
    """Fetch evaluation ratings from Coda academic stream table."""

    # Column ID mappings for the academic stream evaluations table
    COLUMN_IDS = {
        # Paper identification
        'paper_name': 'c-xYDUh_sua3',
        'paper_link': 'c-3KlPoVBu2s',

        # Evaluator identification
        'evaluator_name': 'c-HR_jk43jHl',
        'evaluator_code': 'c-Dz8AXps2lJ',

        # Overall assessment (0-100 percentile)
        'overall_mid': 'c-hDe0joSR7O',
        'overall_lower': 'c-z_-tQdaSVh',
        'overall_upper': 'c-0mSk2aERnA',

        # Claims/Evidence (0-100 percentile)
        'claims_mid': 'c-vaEM_JznKA',
        'claims_lower': 'c-_gqwvPxxJ_',
        'claims_upper': 'c-7ca2UzuE_J',

        # Methods (0-100 percentile)
        'methods_mid': 'c-JxWLl9ykA0',
        'methods_lower': 'c-kSvKt3UdBQ',
        'methods_upper': 'c-kpr9GCbP2E',

        # Advancing Knowledge (0-100 percentile)
        'advancing_mid': 'c-DrnkcYedHI',
        'advancing_lower': 'c-tTec_l31EZ',
        'advancing_upper': 'c-PwQIFZR7J6',

        # Logic & Communication (0-100 percentile)
        'logic_mid': 'c-QoWKXoR_Sa',
        'logic_lower': 'c-O3YkFLWe2K',
        'logic_upper': 'c-Gxh59FHTfE',

        # Open, Collaborative, Replicable (0-100 percentile)
        'open_mid': 'c-6urZCDvwZD',
        'open_lower': 'c-NJwZ6pil5O',
        'open_upper': 'c-D4liJ-Rfop',

        # Relevance to Global Priorities (0-100 percentile)
        'relevance_mid': 'c-bBbRZ67z8j',
        'relevance_lower': 'c-z-bsH6fMTS',
        'relevance_upper': 'c-RW1C_8NkMi',

        # Journal tier ratings (0-5 scale)
        'journal_normative_mid': 'c-9BLi_pANzK',
        'journal_normative_lower': 'c-umIIYehE1d',
        'journal_normative_upper': 'c-EpcbFzgyz_',
        'journal_predicted_mid': 'c-HkGe31LhCv',
        'journal_predicted_lower': 'c-f7HdWgus-i',
        'journal_predicted_upper': 'c-nzlcbluRon',

        # Evaluation content
        'summary': 'c-aGM5wFNlxN',
        'evaluation_text': 'c-SPLYDqD_JC',
        'evaluation_file': 'c-QtN6-2JN6y',

        # Comments on ratings
        'comment_overall': 'c-ZlM46MZhUh',
        'comment_claims': 'c-bTp27iniJr',
        'comment_methods': 'c-YRL_hssl9-',
        'comment_advancing': 'c-mFAAkn5Xpb',
        'comment_logic': 'c-batmKbRMIO',
        'comment_open': 'c-GnogS7woRW',
        'comment_relevance': 'c-9l_589Zgjp',
        'comment_journal': 'c-Nh0qIK9SDX',

        # Metadata
        'date_entered': 'c-XfIDQoDgCH',
        'field_expertise': 'c-o-IHHRlP8r',
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        doc_id: Optional[str] = None,
        table_id: Optional[str] = None
    ):
        """
        Initialize the Coda ratings fetcher.

        Args:
            api_key: Coda API key (defaults to CODA_API_KEY env var)
            doc_id: Coda document ID (defaults to CODA_DOC_ID env var)
            table_id: Coda table ID (defaults to CODA_TABLE_ID env var)
        """
        self.api_key = api_key or os.getenv('CODA_API_KEY')
        self.doc_id = doc_id or os.getenv('CODA_DOC_ID')
        self.table_id = table_id or os.getenv('CODA_TABLE_ID')

        if not self.api_key:
            raise ValueError("CODA_API_KEY not set")
        if not self.doc_id:
            raise ValueError("CODA_DOC_ID not set")
        if not self.table_id:
            raise ValueError("CODA_TABLE_ID not set")

        self.headers = {'Authorization': f'Bearer {self.api_key}'}
        self.base_url = f'https://coda.io/apis/v1/docs/{self.doc_id}/tables/{self.table_id}'

    def _get_value(self, row_values: Dict, key: str) -> Any:
        """Get a value from row data using our column key mapping."""
        col_id = self.COLUMN_IDS.get(key)
        if col_id:
            return row_values.get(col_id)
        return None

    def _parse_rating(
        self,
        row_values: Dict,
        mid_key: str,
        lower_key: str,
        upper_key: str
    ) -> Optional[Dict]:
        """Parse a rating with confidence interval from row data."""
        mid = self._get_value(row_values, mid_key)
        lower = self._get_value(row_values, lower_key)
        upper = self._get_value(row_values, upper_key)

        # Skip if no mid value
        if mid is None or mid == '':
            return None

        return {
            'lower': lower if lower not in [None, ''] else None,
            'mid': mid,
            'upper': upper if upper not in [None, ''] else None,
        }

    def _row_to_evaluation(self, row: Dict) -> Dict:
        """Convert a Coda row to an evaluation data structure."""
        values = row.get('values', {})

        # Build ratings dict
        ratings = {}

        # Overall assessment
        overall = self._parse_rating(values, 'overall_mid', 'overall_lower', 'overall_upper')
        if overall:
            ratings['overall_assessment'] = overall

        # Claims/Evidence
        claims = self._parse_rating(values, 'claims_mid', 'claims_lower', 'claims_upper')
        if claims:
            ratings['claims_evidence'] = claims

        # Methods
        methods = self._parse_rating(values, 'methods_mid', 'methods_lower', 'methods_upper')
        if methods:
            ratings['methods'] = methods

        # Advancing Knowledge
        advancing = self._parse_rating(values, 'advancing_mid', 'advancing_lower', 'advancing_upper')
        if advancing:
            ratings['advancing_knowledge'] = advancing

        # Logic & Communication
        logic = self._parse_rating(values, 'logic_mid', 'logic_lower', 'logic_upper')
        if logic:
            ratings['logic_communication'] = logic

        # Open, Collaborative, Replicable
        open_collab = self._parse_rating(values, 'open_mid', 'open_lower', 'open_upper')
        if open_collab:
            ratings['open_collaborative'] = open_collab

        # Relevance to Global Priorities
        relevance = self._parse_rating(values, 'relevance_mid', 'relevance_lower', 'relevance_upper')
        if relevance:
            ratings['relevance_to_global_priorities'] = relevance

        # Journal tier (normative)
        journal_norm = self._parse_rating(
            values, 'journal_normative_mid', 'journal_normative_lower', 'journal_normative_upper'
        )
        if journal_norm:
            ratings['journal_tier_normative'] = journal_norm

        # Journal tier (predicted/predictive)
        journal_pred = self._parse_rating(
            values, 'journal_predicted_mid', 'journal_predicted_lower', 'journal_predicted_upper'
        )
        if journal_pred:
            ratings['journal_tier_predictive'] = journal_pred

        return {
            'paper_name': self._get_value(values, 'paper_name'),
            'paper_link': self._get_value(values, 'paper_link'),
            'evaluator_name': self._get_value(values, 'evaluator_name'),
            'evaluator_code': self._get_value(values, 'evaluator_code'),
            'summary': self._get_value(values, 'summary'),
            'ratings': ratings,
            'comments': {
                'overall': self._get_value(values, 'comment_overall'),
                'claims': self._get_value(values, 'comment_claims'),
                'methods': self._get_value(values, 'comment_methods'),
                'advancing': self._get_value(values, 'comment_advancing'),
                'logic': self._get_value(values, 'comment_logic'),
                'open': self._get_value(values, 'comment_open'),
                'relevance': self._get_value(values, 'comment_relevance'),
                'journal': self._get_value(values, 'comment_journal'),
            },
            'date_entered': self._get_value(values, 'date_entered'),
            'field_expertise': self._get_value(values, 'field_expertise'),
            'coda_row_id': row.get('id'),
        }

    def get_all_evaluations(self) -> List[Dict]:
        """Fetch all evaluations from the table."""
        all_rows = []
        next_page = None

        while True:
            url = f'{self.base_url}/rows'
            params = {}
            if next_page:
                params['pageToken'] = next_page

            resp = requests.get(url, headers=self.headers, params=params)
            resp.raise_for_status()
            data = resp.json()

            all_rows.extend(data.get('items', []))
            next_page = data.get('nextPageToken')

            if not next_page:
                break

        return [self._row_to_evaluation(row) for row in all_rows]

    def get_evaluations_for_paper(self, paper_name: str) -> List[Dict]:
        """
        Get all evaluations for a specific paper.

        Args:
            paper_name: Name/title of the paper (partial match supported)

        Returns:
            List of evaluation dicts for the paper
        """
        all_evals = self.get_all_evaluations()

        # Filter by paper name (case-insensitive partial match)
        paper_name_lower = paper_name.lower()
        matching = [
            e for e in all_evals
            if e['paper_name'] and paper_name_lower in e['paper_name'].lower()
        ]

        return matching

    def get_ratings_for_paper(self, paper_name: str) -> Dict[str, Dict]:
        """
        Get ratings for a paper formatted for RatingsTableGenerator.

        Args:
            paper_name: Name/title of the paper

        Returns:
            Dict mapping evaluator identifier to their ratings
            Format: {'Evaluator 1': {'overall_assessment': {...}, ...}, ...}
        """
        evaluations = self.get_evaluations_for_paper(paper_name)

        result = {}
        for i, eval_data in enumerate(evaluations, 1):
            # Use evaluator name if public, otherwise use code or number
            evaluator_id = (
                eval_data['evaluator_name']
                or eval_data['evaluator_code']
                or f"Evaluator {i}"
            )
            result[evaluator_id] = eval_data['ratings']

        return result

    def list_papers(self) -> List[str]:
        """Get list of all unique paper names in the table."""
        all_evals = self.get_all_evaluations()
        papers = set(e['paper_name'] for e in all_evals if e['paper_name'])
        return sorted(papers)


def generate_ratings_table_for_paper(
    paper_name: str,
    anonymous: bool = False,
    include_journal_tiers: bool = True
) -> str:
    """
    Generate a markdown ratings comparison table for a paper.

    This is a convenience function that fetches ratings from Coda
    and generates a formatted markdown table.

    Args:
        paper_name: Name/title of the paper (partial match supported)
        anonymous: If True, use "Evaluator 1", "Evaluator 2" instead of names
        include_journal_tiers: If True, include journal tier predictions

    Returns:
        Markdown table string ready for PubPub

    Example:
        table = generate_ratings_table_for_paper("Climate Change")
        print(table)
    """
    # Import here to avoid circular imports
    import sys
    from pathlib import Path
    # Add parent directory to path for imports
    scripts_dir = Path(__file__).parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from pubpub_automation.ratings_table_generator import RatingsTableGenerator

    fetcher = CodaRatingsFetcher()
    evaluations = fetcher.get_evaluations_for_paper(paper_name)

    if not evaluations:
        return f"No evaluations found for paper matching: {paper_name}"

    # Build ratings dict with appropriate evaluator names
    ratings_by_evaluator = {}
    for i, eval_data in enumerate(evaluations, 1):
        if anonymous:
            evaluator_id = f"Evaluator {i}"
        else:
            evaluator_id = (
                eval_data['evaluator_name']
                or eval_data['evaluator_code']
                or f"Evaluator {i}"
            )

        ratings = eval_data['ratings'].copy()

        # Optionally remove journal tiers
        if not include_journal_tiers:
            ratings.pop('journal_tier_normative', None)
            ratings.pop('journal_tier_predicted', None)

        ratings_by_evaluator[evaluator_id] = ratings

    # Generate table
    generator = RatingsTableGenerator()
    return generator.generate_comparison_table(ratings_by_evaluator)


def main():
    """Example usage and testing."""
    fetcher = CodaRatingsFetcher()

    # List all papers
    print("Papers in database:")
    print("=" * 60)
    papers = fetcher.list_papers()
    for p in papers[:10]:
        print(f"  - {p}")
    if len(papers) > 10:
        print(f"  ... and {len(papers) - 10} more")

    print()

    # Get evaluations for a specific paper
    if papers:
        test_paper = papers[0]
        print(f"Evaluations for: {test_paper}")
        print("=" * 60)

        evals = fetcher.get_evaluations_for_paper(test_paper)
        for e in evals:
            print(f"\nEvaluator: {e['evaluator_name'] or e['evaluator_code'] or 'Anonymous'}")
            print(f"Ratings:")
            for criterion, rating in e['ratings'].items():
                print(f"  {criterion}: {rating}")

        print()

        # Generate a complete markdown table
        print("Generated Markdown Table:")
        print("=" * 60)
        table = generate_ratings_table_for_paper(test_paper)
        print(table)

        print()
        print("Anonymous version:")
        print("=" * 60)
        anon_table = generate_ratings_table_for_paper(test_paper, anonymous=True)
        print(anon_table)


if __name__ == '__main__':
    main()
