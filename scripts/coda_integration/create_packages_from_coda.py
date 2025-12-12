#!/usr/bin/env python3
"""
Create PubPub Evaluation Packages from Coda Data

This script provides a complete workflow to:
1. List and select papers from Coda
2. Fetch evaluation ratings for selected papers
3. Generate ratings tables
4. Create complete PubPub evaluation packages

Usage:
    # Interactive mode - select papers
    python create_packages_from_coda.py

    # Specify papers directly
    python create_packages_from_coda.py --papers "Climate Change" "Scale-Use Heterogeneity"

    # List available papers
    python create_packages_from_coda.py --list
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fetch_ratings import CodaRatingsFetcher, generate_ratings_table_for_paper

load_dotenv()


@dataclass
class PackageConfig:
    """Configuration for creating an evaluation package."""
    paper_name: str
    draft_mode: bool = True
    include_journal_tiers: bool = True
    anonymous_evaluators: bool = False


class CodaToPubPubCreator:
    """Create PubPub evaluation packages from Coda data."""

    def __init__(
        self,
        pubpub_email: Optional[str] = None,
        pubpub_password: Optional[str] = None,
        pubpub_community_url: Optional[str] = None,
        pubpub_community_id: Optional[str] = None
    ):
        """
        Initialize with PubPub credentials.

        Args:
            pubpub_email: PubPub login email (or PUBPUB_EMAIL env var)
            pubpub_password: PubPub password (or PUBPUB_PASSWORD env var)
            pubpub_community_url: Community URL (or PUBPUB_COMMUNITY_URL env var)
            pubpub_community_id: Community ID (or PUBPUB_COMMUNITY_ID env var)
        """
        self.email = pubpub_email or os.getenv('PUBPUB_EMAIL')
        self.password = pubpub_password or os.getenv('PUBPUB_PASSWORD')
        self.community_url = pubpub_community_url or os.getenv('PUBPUB_COMMUNITY_URL')
        self.community_id = pubpub_community_id or os.getenv('PUBPUB_COMMUNITY_ID')

        self.coda_fetcher = CodaRatingsFetcher()
        self._pubhelper = None

    @property
    def pubhelper(self):
        """Lazy-load PubPub helper."""
        if self._pubhelper is None:
            if not all([self.email, self.password, self.community_url, self.community_id]):
                raise ValueError(
                    "PubPub credentials required. Set PUBPUB_EMAIL, PUBPUB_PASSWORD, "
                    "PUBPUB_COMMUNITY_URL, and PUBPUB_COMMUNITY_ID in .env"
                )
            from pypubpub import Pubshelper_v6
            self._pubhelper = Pubshelper_v6(
                community_url=self.community_url,
                community_id=self.community_id,
                email=self.email,
                password=self.password
            )
            self._pubhelper.login()
        return self._pubhelper

    def list_papers(self) -> List[str]:
        """Get list of all papers with evaluations in Coda."""
        return self.coda_fetcher.list_papers()

    def get_paper_info(self, paper_name: str) -> Dict:
        """
        Get detailed info about evaluations for a paper.

        Args:
            paper_name: Paper name (partial match supported)

        Returns:
            Dict with paper info and evaluation count
        """
        evals = self.coda_fetcher.get_evaluations_for_paper(paper_name)
        if not evals:
            return {'found': False, 'paper_name': paper_name}

        return {
            'found': True,
            'paper_name': evals[0]['paper_name'],
            'paper_link': evals[0].get('paper_link'),
            'evaluation_count': len(evals),
            'evaluators': [
                e['evaluator_name'] or e['evaluator_code'] or 'Anonymous'
                for e in evals
            ],
            'has_public_evaluators': any(e['evaluator_name'] for e in evals)
        }

    def generate_ratings_table(
        self,
        paper_name: str,
        anonymous: bool = False,
        include_journal_tiers: bool = True
    ) -> str:
        """
        Generate markdown ratings table for a paper.

        Args:
            paper_name: Paper name (partial match)
            anonymous: Use "Evaluator 1" etc instead of names
            include_journal_tiers: Include journal tier predictions

        Returns:
            Markdown table string
        """
        return generate_ratings_table_for_paper(
            paper_name,
            anonymous=anonymous,
            include_journal_tiers=include_journal_tiers
        )

    def generate_tables_for_papers(
        self,
        paper_names: List[str],
        anonymous: bool = False,
        include_journal_tiers: bool = True
    ) -> Dict[str, str]:
        """
        Generate ratings tables for multiple papers.

        Args:
            paper_names: List of paper names (partial matches)
            anonymous: Use anonymous evaluator labels
            include_journal_tiers: Include journal tier predictions

        Returns:
            Dict mapping paper name to markdown table
        """
        results = {}
        for paper in paper_names:
            print(f"Generating table for: {paper}")
            table = self.generate_ratings_table(
                paper,
                anonymous=anonymous,
                include_journal_tiers=include_journal_tiers
            )
            # Get the actual paper name from Coda
            evals = self.coda_fetcher.get_evaluations_for_paper(paper)
            actual_name = evals[0]['paper_name'] if evals else paper
            results[actual_name] = table
        return results

    def create_package(
        self,
        paper_name: str,
        draft_mode: bool = True,
        evaluation_manager_id: Optional[str] = None
    ) -> Dict:
        """
        Create a complete PubPub evaluation package from Coda data.

        Args:
            paper_name: Paper name in Coda (partial match)
            draft_mode: If True, use anonymous evaluators
            evaluation_manager_id: PubPub user ID for evaluation manager

        Returns:
            Dict with created pub info
        """
        from pypubpub.Pubv6 import EvaluationPackage
        from pubpub_automation.package_assembler import (
            PaperMetadata, EvaluationData, EvaluationPackageData
        )

        # Fetch evaluations from Coda
        evaluations = self.coda_fetcher.get_evaluations_for_paper(paper_name)
        if not evaluations:
            raise ValueError(f"No evaluations found for: {paper_name}")

        actual_paper_name = evaluations[0]['paper_name']
        paper_link = evaluations[0].get('paper_link')

        print(f"\n{'='*60}")
        print(f"Creating Package: {actual_paper_name}")
        print(f"Evaluations: {len(evaluations)}")
        print(f"Mode: {'DRAFT' if draft_mode else 'FINAL'}")
        print(f"{'='*60}\n")

        # Build evaluation configs
        eval_configs = []
        eval_data_list = []

        for i, eval_data in enumerate(evaluations, 1):
            evaluator_name = eval_data['evaluator_name']
            evaluator_code = eval_data['evaluator_code']

            # In draft mode, don't include names
            if draft_mode:
                eval_configs.append({})
            else:
                config = {}
                if evaluator_name:
                    config['author'] = {'name': evaluator_name}
                eval_configs.append(config)

            # Build EvaluationData for content generation
            eval_data_obj = EvaluationData(
                ratings=eval_data['ratings'],
                review_text=eval_data.get('summary', ''),
                evaluator_name=evaluator_name if not draft_mode else None,
                is_public=bool(evaluator_name) and not draft_mode
            )
            eval_data_list.append(eval_data_obj)

        # Create PubPub package structure
        print("Creating PubPub package structure...")

        # Try to extract DOI from link
        doi = None
        if paper_link:
            if 'doi.org' in paper_link:
                doi = paper_link.split('doi.org/')[-1]
            elif '10.' in paper_link:
                # Try to find DOI pattern in URL
                import re
                doi_match = re.search(r'10\.\d{4,}/[^\s]+', paper_link)
                if doi_match:
                    doi = doi_match.group()

        print(f"  Paper: {actual_paper_name}")
        print(f"  Link: {paper_link}")
        print(f"  DOI: {doi or 'None (using URL/title)'}")

        pkg = EvaluationPackage(
            doi=doi,
            url=paper_link,
            title=actual_paper_name,
            evaluation_manager_author=evaluation_manager_id or {},
            evaluations=eval_configs,
            email=self.email,
            password=self.password,
            community_url=self.community_url,
            community_id=self.community_id,
            autorun=True
        )

        print(f"  Created summary pub: {pkg.eval_summ_pub['slug']}")
        for i, (pub_id, pub_obj) in enumerate(pkg.activePubs, 1):
            print(f"  Created evaluation {i} pub: {pub_obj['slug']}")

        # Use TemplateGenerator to create properly formatted content
        print("\nGenerating content using templates...")
        from pubpub_automation.template_generator import TemplateGenerator
        from pubpub_automation.markdown_to_prosemirror import markdown_to_prosemirror

        template_gen = TemplateGenerator()

        # Build paper_info dict for template generator
        paper_info = {
            'title': actual_paper_name,
            'url': paper_link,
            'doi': doi,
        }

        # Build evaluations list for template generator
        eval_data_for_template = []
        for i, eval_data in enumerate(evaluations, 1):
            eval_entry = {
                'name': eval_data['evaluator_name'] or f"Evaluator {i}",
                'is_public': not draft_mode and bool(eval_data['evaluator_name']),
                'ratings': eval_data['ratings'],
                'review_text': eval_data.get('summary', ''),
                'comments': None,  # Combine comments if available
            }

            # Combine rating comments into additional comments
            comments = eval_data.get('comments', {})
            comment_parts = []
            for criterion, comment in comments.items():
                if comment:
                    comment_parts.append(f"**{criterion.replace('_', ' ').title()}:** {comment}")
            if comment_parts:
                eval_entry['comments'] = "\n\n".join(comment_parts)

            eval_data_for_template.append(eval_entry)

        # Generate complete package using template generator
        package_content = template_gen.generate_complete_package(
            paper_info=paper_info,
            evaluations=eval_data_for_template,
            manager_summary=None  # Can be added later
        )

        # Import summary content
        print("Importing summary content...")
        summary_doc = markdown_to_prosemirror(package_content['summary'])
        self.pubhelper.replace_pub_text(
            pubId=pkg.eval_summ_pub['id'],
            attributes=None,
            doc=summary_doc
        )
        print(f"  Summary content imported ({len(package_content['summary'])} chars)")

        # Import individual evaluation content
        print("Importing evaluation content...")
        for i, ((pub_id, pub_obj), eval_markdown) in enumerate(zip(pkg.activePubs, package_content['evaluations']), 1):
            eval_doc = markdown_to_prosemirror(eval_markdown)
            self.pubhelper.replace_pub_text(
                pubId=pub_id,
                attributes=None,
                doc=eval_doc
            )
            print(f"  Evaluation {i} content imported ({len(eval_markdown)} chars)")

        # Return package info
        result = {
            'paper_name': actual_paper_name,
            'summary_pub_id': pkg.eval_summ_pub['id'],
            'summary_slug': pkg.eval_summ_pub['slug'],
            'summary_url': f"{self.community_url}/pub/{pkg.eval_summ_pub['slug']}",
            'evaluation_pubs': [
                {
                    'id': pub_id,
                    'slug': pub_obj['slug'],
                    'url': f"{self.community_url}/pub/{pub_obj['slug']}"
                }
                for (pub_id, pub_obj) in pkg.activePubs
            ],
            'content': package_content
        }

        print(f"\n{'='*60}")
        print("Package created!")
        print(f"Summary: {result['summary_url']}")
        for i, pub in enumerate(result['evaluation_pubs'], 1):
            print(f"Evaluation {i}: {pub['url']}")
        print(f"{'='*60}\n")

        return result

    def create_packages_batch(
        self,
        paper_names: List[str],
        draft_mode: bool = True,
        evaluation_manager_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Create multiple evaluation packages.

        Args:
            paper_names: List of paper names
            draft_mode: Use anonymous evaluators
            evaluation_manager_id: PubPub user ID for manager

        Returns:
            List of created package info dicts
        """
        results = []
        for paper in paper_names:
            try:
                result = self.create_package(
                    paper,
                    draft_mode=draft_mode,
                    evaluation_manager_id=evaluation_manager_id
                )
                results.append(result)
            except Exception as e:
                print(f"ERROR creating package for {paper}: {e}")
                results.append({'paper_name': paper, 'error': str(e)})
        return results


def interactive_select_papers(creator: CodaToPubPubCreator) -> List[str]:
    """Interactive paper selection."""
    papers = creator.list_papers()

    print("\nAvailable papers:")
    print("-" * 60)
    for i, paper in enumerate(papers, 1):
        info = creator.get_paper_info(paper)
        eval_count = info.get('evaluation_count', 0)
        print(f"  {i:3}. {paper[:50]}{'...' if len(paper) > 50 else ''} ({eval_count} evals)")

    print("\nEnter paper numbers separated by commas (e.g., 1,3,5)")
    print("Or enter 'all' to select all papers")
    print("Or enter partial paper names separated by semicolons")

    selection = input("\nSelection: ").strip()

    if selection.lower() == 'all':
        return papers

    if ',' in selection and selection.replace(',', '').replace(' ', '').isdigit():
        # Numeric selection
        indices = [int(x.strip()) - 1 for x in selection.split(',')]
        return [papers[i] for i in indices if 0 <= i < len(papers)]

    if ';' in selection:
        # Name-based selection
        return [name.strip() for name in selection.split(';')]

    # Single selection - could be number or name
    if selection.isdigit():
        idx = int(selection) - 1
        if 0 <= idx < len(papers):
            return [papers[idx]]

    return [selection]


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Create PubPub evaluation packages from Coda data'
    )
    parser.add_argument(
        '--list', action='store_true',
        help='List all papers with evaluations'
    )
    parser.add_argument(
        '--papers', nargs='+',
        help='Paper names to process (partial match supported)'
    )
    parser.add_argument(
        '--tables-only', action='store_true',
        help='Only generate ratings tables, do not create PubPub packages'
    )
    parser.add_argument(
        '--draft', action='store_true', default=True,
        help='Draft mode - use anonymous evaluators (default)'
    )
    parser.add_argument(
        '--final', action='store_true',
        help='Final mode - include evaluator names'
    )
    parser.add_argument(
        '--anonymous', action='store_true',
        help='Use anonymous evaluator labels in tables'
    )
    parser.add_argument(
        '--no-journal-tiers', action='store_true',
        help='Exclude journal tier predictions from tables'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file for tables (default: print to stdout)'
    )

    args = parser.parse_args()

    creator = CodaToPubPubCreator()

    # List papers
    if args.list:
        papers = creator.list_papers()
        print(f"\nPapers with evaluations ({len(papers)} total):")
        print("=" * 60)
        for paper in papers:
            info = creator.get_paper_info(paper)
            eval_count = info.get('evaluation_count', 0)
            evaluators = info.get('evaluators', [])
            print(f"\n{paper}")
            print(f"  Evaluations: {eval_count}")
            print(f"  Evaluators: {', '.join(evaluators[:3])}{'...' if len(evaluators) > 3 else ''}")
        return

    # Get papers to process
    if args.papers:
        selected_papers = args.papers
    else:
        selected_papers = interactive_select_papers(creator)

    if not selected_papers:
        print("No papers selected.")
        return

    print(f"\nSelected {len(selected_papers)} paper(s)")

    # Determine mode
    draft_mode = not args.final
    anonymous = args.anonymous or draft_mode

    # Generate tables only
    if args.tables_only:
        tables = creator.generate_tables_for_papers(
            selected_papers,
            anonymous=anonymous,
            include_journal_tiers=not args.no_journal_tiers
        )

        output = ""
        for paper_name, table in tables.items():
            output += f"\n## {paper_name}\n\n{table}\n\n"

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Tables saved to: {args.output}")
        else:
            print(output)
        return

    # Create full packages
    print("\nCreating PubPub packages...")
    results = creator.create_packages_batch(
        selected_papers,
        draft_mode=draft_mode
    )

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    successful = [r for r in results if 'error' not in r]
    failed = [r for r in results if 'error' in r]

    print(f"Created: {len(successful)} packages")
    if failed:
        print(f"Failed: {len(failed)} packages")
        for r in failed:
            print(f"  - {r['paper_name']}: {r['error']}")

    if successful:
        print("\nCreated packages:")
        for r in successful:
            print(f"  - {r['paper_name']}")
            print(f"    Summary: {r['summary_url']}")


if __name__ == '__main__':
    main()
