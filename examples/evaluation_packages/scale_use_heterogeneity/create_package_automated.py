#!/usr/bin/env python3
"""
Create Scale-Use Heterogeneity Evaluation Package (Automated)

This script demonstrates the complete automation for creating
the Caspar Kaiser and Alberto Prati evaluation package.

This is a SPECIFIC EXAMPLE - the general automation is in:
  scripts/pubpub_automation/create_package_from_data.py
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts' / 'pubpub_automation'))

from package_assembler import PaperMetadata, EvaluationData, EvaluationPackageData
from create_package_from_data import EvaluationPackageCreator

# Import credentials (NOT committed to repo)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'unjournalpubpub_production_moved'))
import conf


def create_caspar_prati_package(draft_mode: bool = True):
    """
    Create evaluation package for Caspar Kaiser and Alberto Prati's
    evaluation of "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"

    Args:
        draft_mode: If True, don't add evaluator names (for initial author response)
    """

    # Paper metadata
    paper = PaperMetadata(
        title='Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being',
        authors=[
            'Daniel J. Benjamin',
            'Kristen Cooper',
            'Ori Heffetz',
            'Miles S. Kimball',
            'Jiannan Zhou'
        ],
        doi='10.3386/w31728'
    )

    # Caspar Kaiser's evaluation
    caspar_evaluation = EvaluationData(
        ratings={
            'overall_assessment': {'lower': 80, 'mid': 95, 'upper': 100},
            'advancing_knowledge': {'lower': 90, 'mid': 95, 'upper': 100},
            'methods': {'lower': 80, 'mid': 90, 'upper': 100},
            'logic_communication': {'lower': 70, 'mid': 80, 'upper': 90},
            'open_collaborative': {'lower': 60, 'mid': 75, 'upper': 90},
            'real_world_relevance': {'lower': 70, 'mid': 80, 'upper': 90},
            'relevance_to_global_priorities': {'lower': 40, 'mid': 60, 'upper': 80},
            'claims_evidence': {'lower': 70, 'mid': 80, 'upper': 90},
            'journal_merit': {'lower': 4.1, 'mid': 4.7, 'upper': 5.0},
        },
        evaluator_name='Caspar Kaiser',
        evaluator_affiliation='Unknown',  # TODO: Get from Caspar
        evaluator_orcid=None,  # TODO: Get from Caspar
        is_public=False,  # Will be set to True after author response if Caspar consents
        review_source_type='latex',
        review_source_path=Path('/tmp/review_data/main.tex')
    )

    # Alberto Prati's evaluation
    # TODO: Extract complete ratings from Prati's PDF
    # TODO: Get Prati's written evaluation (if exists)
    prati_evaluation = EvaluationData(
        ratings={
            'overall_assessment': {'lower': 90, 'mid': 95, 'upper': 100},
            # Other ratings need to be extracted from PDF
        },
        evaluator_name='Alberto Prati',
        evaluator_affiliation='Unknown',  # TODO: Get from Prati
        evaluator_orcid=None,  # TODO: Get from Prati
        is_public=False,  # Will be set to True after author response if Prati consents
        review_text=None,  # TODO: Get written evaluation if exists
    )

    # Package data
    package_data = EvaluationPackageData(
        paper=paper,
        evaluations=[caspar_evaluation, prati_evaluation],
        manager_summary=None,  # TODO: Add manager summary
        evaluation_manager=None  # TODO: Add manager ID if needed
    )

    # Create package creator
    creator = EvaluationPackageCreator(
        email=conf.email,
        password=conf.password,
        community_url=conf.community_url,
        community_id=conf.community_id
    )

    # Create package
    output_dir = Path(__file__).parent / 'output'
    result = creator.create_package(
        package_data=package_data,
        draft_mode=draft_mode,
        output_dir=output_dir
    )

    print(f"\n{'='*60}")
    print("Package Information")
    print(f"{'='*60}")
    print(f"Summary URL: {conf.community_url}/pub/{result['summary_slug']}")
    for i, eval_pub in enumerate(result['evaluation_pubs'], 1):
        print(f"Evaluation {i} URL: {conf.community_url}/pub/{eval_pub['slug']}")
    print(f"\nMarkdown files saved to: {output_dir}")
    print(f"{'='*60}\n")

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Create Caspar & Prati evaluation package'
    )
    parser.add_argument(
        '--final',
        action='store_true',
        help='Final mode (add evaluator names - use AFTER author response)'
    )

    args = parser.parse_args()

    # Create package
    result = create_caspar_prati_package(draft_mode=not args.final)

    if args.final:
        print("\n⚠️  FINAL MODE: Evaluator names will be added")
        print("   Make sure evaluators have consented to be identified!")
    else:
        print("\n✓ DRAFT MODE: Package created without evaluator names")
        print("  Share with authors for response")
        print("  Re-run with --final after author response to add names")
