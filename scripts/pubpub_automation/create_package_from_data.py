#!/usr/bin/env python3
"""
Create Evaluation Package from Data

Main automation script that:
1. Assembles markdown from various sources (Coda, LaTeX, PDFs)
2. Creates PubPub package structure
3. Imports markdown content into PubPub
4. Sets up metadata, connections, and attributions

This is the general-purpose script for any evaluation package.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pypubpub import Pubshelper_v6
from pypubpub.Pubv6 import EvaluationPackage

from package_assembler import PackageAssembler, PaperMetadata, EvaluationData, EvaluationPackageData


class EvaluationPackageCreator:
    """Creates complete evaluation packages in PubPub."""

    def __init__(
        self,
        email: str,
        password: str,
        community_url: str,
        community_id: str
    ):
        """
        Initialize creator with PubPub credentials.

        Args:
            email: PubPub login email
            password: PubPub password
            community_url: Community URL (e.g., 'https://unjournal.pubpub.org')
            community_id: Community UUID
        """
        self.pubhelper = Pubshelper_v6(
            community_url=community_url,
            community_id=community_id,
            email=email,
            password=password
        )
        self.pubhelper.login()
        self.assembler = PackageAssembler()

    def create_package(
        self,
        package_data: EvaluationPackageData,
        draft_mode: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict:
        """
        Create complete evaluation package in PubPub.

        Args:
            package_data: Complete package data
            draft_mode: If True, don't publish evaluator names yet
            output_dir: Optional directory to save markdown files

        Returns:
            Dict with created pub IDs and info
        """
        print(f"\n{'='*60}")
        print(f"Creating Evaluation Package")
        print(f"Paper: {package_data.paper.title}")
        print(f"Evaluations: {len(package_data.evaluations)}")
        print(f"Mode: {'DRAFT (anonymous)' if draft_mode else 'FINAL (with names)'}")
        print(f"{'='*60}\n")

        # Step 1: Assemble markdown content
        print("Step 1: Assembling markdown content...")
        package_markdown = self.assembler.assemble_from_data(package_data, output_dir)
        print(f"  ✓ Generated summary ({len(package_markdown['summary'])} chars)")
        print(f"  ✓ Generated {len(package_markdown['evaluations'])} evaluation(s)")

        # Step 2: Create PubPub package structure
        print("\nStep 2: Creating PubPub package structure...")

        # Prepare evaluation configs for EvaluationPackage
        eval_configs = []
        for i, evaluation in enumerate(package_data.evaluations):
            # In draft mode or if not public, don't add author info yet
            if draft_mode or not evaluation.is_public:
                eval_configs.append({})  # Empty placeholder
            else:
                # In final mode with public evaluator, add attribution
                eval_config = {}
                if evaluation.evaluator_name:
                    eval_config['author'] = {
                        'name': evaluation.evaluator_name
                    }
                    if evaluation.evaluator_orcid:
                        eval_config['author']['orcid'] = evaluation.evaluator_orcid
                    if evaluation.evaluator_affiliation:
                        eval_config['author']['affiliation'] = evaluation.evaluator_affiliation
                eval_configs.append(eval_config)

        # Create package (structure only, no content yet)
        pkg = EvaluationPackage(
            doi=package_data.paper.doi,
            url=package_data.paper.url if not package_data.paper.doi else None,
            evaluation_manager_author=package_data.evaluation_manager,
            evaluations=eval_configs,
            email=self.pubhelper.email,
            password=self.pubhelper.password,
            community_url=self.pubhelper.community_url,
            community_id=self.pubhelper.community_id,
            autorun=True
        )

        print(f"  ✓ Created evaluation summary pub: {pkg.eval_summ_pub['id']}")
        for i, pub in enumerate(pkg.activePubs, 1):
            print(f"  ✓ Created evaluation {i} pub: {pub['id']}")

        # Step 3: Import markdown content into pubs
        print("\nStep 3: Importing markdown content...")

        # Import summary
        print(f"  Importing summary...")
        self.pubhelper.replace_pub_text(
            pub_id=pkg.eval_summ_pub['id'],
            markdown=package_markdown['summary']
        )
        print(f"    ✓ Summary content imported")

        # Import individual evaluations
        for i, (pub, eval_markdown) in enumerate(zip(pkg.activePubs, package_markdown['evaluations']), 1):
            print(f"  Importing evaluation {i}...")
            self.pubhelper.replace_pub_text(
                pub_id=pub['id'],
                markdown=eval_markdown
            )
            print(f"    ✓ Evaluation {i} content imported")

        # Step 4: Summary
        print(f"\n{'='*60}")
        print("✓ Package creation complete!")
        print(f"{'='*60}\n")

        print("Created publications:")
        print(f"  Summary: {self.pubhelper.community_url}/pub/{pkg.eval_summ_pub['slug']}")
        for i, pub in enumerate(pkg.activePubs, 1):
            print(f"  Evaluation {i}: {self.pubhelper.community_url}/pub/{pub['slug']}")

        if draft_mode:
            print("\n⚠️  DRAFT MODE: Evaluator names not added yet")
            print("   After author response, re-run in final mode to add names")

        # Return package info
        return {
            'summary_pub_id': pkg.eval_summ_pub['id'],
            'summary_slug': pkg.eval_summ_pub['slug'],
            'evaluation_pubs': [
                {'id': pub['id'], 'slug': pub['slug']}
                for pub in pkg.activePubs
            ],
            'package_markdown': package_markdown
        }

    def create_from_coda(
        self,
        coda_data: Dict,
        paper_metadata: PaperMetadata,
        draft_mode: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict:
        """Create package from Coda form data."""
        # Parse Coda data into EvaluationPackageData
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
            manager_summary=coda_data.get('manager_summary'),
            evaluation_manager=coda_data.get('manager_id')
        )

        return self.create_package(package_data, draft_mode, output_dir)

    def create_from_files(
        self,
        paper_metadata: PaperMetadata,
        evaluation_files: List[Dict],
        manager_summary: Optional[str] = None,
        manager_id: Optional[str] = None,
        draft_mode: bool = True,
        output_dir: Optional[Path] = None
    ) -> Dict:
        """Create package from local files."""
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
            manager_summary=manager_summary,
            evaluation_manager=manager_id
        )

        return self.create_package(package_data, draft_mode, output_dir)


def main():
    """Example usage and CLI."""
    import argparse

    parser = argparse.ArgumentParser(description='Create evaluation package in PubPub')
    parser.add_argument('--config', required=True, help='Path to JSON config file')
    parser.add_argument('--draft', action='store_true', help='Draft mode (no evaluator names)')
    parser.add_argument('--output-dir', help='Directory to save markdown files')

    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = json.load(f)

    # Create package creator
    creator = EvaluationPackageCreator(
        email=config['pubpub']['email'],
        password=config['pubpub']['password'],
        community_url=config['pubpub']['community_url'],
        community_id=config['pubpub']['community_id']
    )

    # Parse paper metadata
    paper = PaperMetadata(**config['paper'])

    # Create package from evaluation files
    result = creator.create_from_files(
        paper_metadata=paper,
        evaluation_files=config['evaluations'],
        manager_summary=config.get('manager_summary'),
        manager_id=config.get('manager_id'),
        draft_mode=args.draft,
        output_dir=Path(args.output_dir) if args.output_dir else None
    )

    print("\n✓ Package created successfully!")
    print(f"Summary: {result['summary_slug']}")


if __name__ == '__main__':
    main()
