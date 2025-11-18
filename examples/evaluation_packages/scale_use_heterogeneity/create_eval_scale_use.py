"""
Create evaluation package for "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
Evaluators: Caspar Kaiser and Alberto Prati
"""

import json
from pypubpub import Pubshelper_v6
from pypubpub.Pubv6 import EvaluationPackage, record_pub_conf
import sys
import os

# Add parent directory to path to import conf
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'unjournalpubpub_production_moved'))
from conf import email, password, community_id, community_url

# Configuration
config = record_pub_conf(email, password, community_id, community_url)
print('Config created successfully')

# Paper details
PAPER_TITLE = "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being"
PAPER_DOI = "10.3386/w31728"  # NBER Working Paper
PAPER_AUTHORS = [
    "Daniel J. Benjamin",
    "Kristen Cooper",
    "Ori Heffetz",
    "Miles S. Kimball",
    "Jiannan Zhou"
]

# Evaluator data extracted from forms
EVALUATORS_DATA = {
    "caspar": {
        "name": "Caspar Kaiser",
        "pseudonym": "Friedrich",
        "identified": True,  # Wants to be publicly identified
        "summary": "This is a major methodological innovation in how we can adjust for differences in scale-use. The empirical component would especially benefit from more diverse and reliable samples.",
        "review_file": "/tmp/review_data/main.tex",
        "ratings": {
            "overall_assessment": {"lower": 80, "mid": 95, "upper": 100},
            "claims_evidence": {"lower": 70, "mid": 80, "upper": 90},
            "methods": {"lower": 80, "mid": 90, "upper": 100},
            "advancing_knowledge": {"lower": 80, "mid": 90, "upper": 100},
            "logic_communication": {"lower": 60, "mid": 75, "upper": 90},
            "open_replicable": {"lower": 70, "mid": 85, "upper": 90},
            "relevance_global": {"lower": 0, "mid": 0, "upper": 0},  # Left open
            "journal_merit": {"lower": 4.7, "mid": 4.1, "upper": 5.0},
            "journal_prediction": {"lower": 4.4, "mid": 4.0, "upper": 5.0}
        },
        "comments": {
            "overall": "I know few papers in this specific field from the last few years that are more important than this.",
            "logic_communication": "The reasoning itself, to the extent that I was able to assess it, was sound and very thorough. As noted in my review, the paper itself could have been more accessible.",
            "open_replicable": "The authors have shared the data. I was able to replicate the simplest version of their method using Stata (they were using R). I have not attempted to fully replicate the paper, so cannot comment on this.",
            "relevance": "I left this open because it seems hard to assess. In my mind this is a paper about a fundamental scientific question, which will eventually be of relevance to (policy) practitioners. However, the paper, at present, is not aimed at that."
        },
        "field_years": "Since about 2018",
        "reviews_completed": "10+",
        "time_spent": "8 hours approx."
    },
    "prati": {
        "name": "Alberto Prati",
        "pseudonym": "Prati",
        "identified": True,  # Assuming based on form
        "summary": "",  # To be filled if separate review document found
        "review_file": None,  # No separate review document found yet
        "ratings": {
            "overall_assessment": {"lower": 90, "mid": 95, "upper": 100},
            # Additional ratings to be extracted from full form if available
        }
    }
}

def create_draft_package():
    """
    Create a draft evaluation package with structure but empty evaluations
    This allows sharing with authors before adding evaluator names
    """
    print(f"\nCreating draft evaluation package for: {PAPER_TITLE}")
    print(f"DOI: {PAPER_DOI}")
    print(f"Number of evaluations: {len(EVALUATORS_DATA)}")

    # Create evaluation package with empty placeholders
    # We'll populate the content manually after structure is created
    evaluation_package = EvaluationPackage(
        doi=PAPER_DOI,
        evaluation_manager_author=None,  # To be specified
        evaluations=[
            {},  # Caspar Kaiser - placeholder
            {}   # Alberto Prati - placeholder
        ],
        email=email,
        password=password,
        community_url=community_url,
        community_id=community_id,
        config=config,
        verbose=True,
        autorun=False  # Set to False to review before publishing
    )

    print("\n" + "="*80)
    print("Draft package structure created!")
    print("="*80)
    print("\nNext steps:")
    print("1. Review the created structure in PubPub")
    print("2. Add evaluation content from the evaluators")
    print("3. Add ratings tables using the data above")
    print("4. Share with authors for response")
    print("5. After author response, add evaluator names if they want to be identified")

    return evaluation_package

def export_ratings_table():
    """Export ratings in a format suitable for PubPub tables"""
    print("\n" + "="*80)
    print("RATINGS TABLE FOR PUBPUB")
    print("="*80)

    for eval_id, data in EVALUATORS_DATA.items():
        print(f"\n### {data['name']} ({data['pseudonym']})")
        print("\nOverall Assessment (percentile):")
        print(f"  Lower 90% CI: {data['ratings']['overall_assessment']['lower']}")
        print(f"  Midpoint: {data['ratings']['overall_assessment']['mid']}")
        print(f"  Upper 90% CI: {data['ratings']['overall_assessment']['upper']}")

        if 'claims_evidence' in data['ratings']:
            print("\nClaims, Evidence & Reasoning:")
            print(f"  Lower: {data['ratings']['claims_evidence']['lower']}")
            print(f"  Mid: {data['ratings']['claims_evidence']['mid']}")
            print(f"  Upper: {data['ratings']['claims_evidence']['upper']}")

        # Add more ratings as needed

    # Create markdown table format
    print("\n\n### Markdown Table Format:")
    print("| Criterion | Evaluator | Lower CI | Midpoint | Upper CI |")
    print("|-----------|-----------|----------|----------|----------|")

    for eval_id, data in EVALUATORS_DATA.items():
        ratings = data['ratings']
        print(f"| Overall Assessment | {data['pseudonym']} | {ratings['overall_assessment']['lower']} | {ratings['overall_assessment']['mid']} | {ratings['overall_assessment']['upper']} |")

        if 'claims_evidence' in ratings:
            print(f"| Claims & Evidence | {data['pseudonym']} | {ratings['claims_evidence']['lower']} | {ratings['claims_evidence']['mid']} | {ratings['claims_evidence']['upper']} |")

if __name__ == "__main__":
    print("="*80)
    print("SCALE-USE HETEROGENEITY EVALUATION PACKAGE")
    print("="*80)

    # Export ratings for reference
    export_ratings_table()

    # Create the draft package
    print("\n\nReady to create draft package? This will create the structure on PubPub.")
    response = input("Proceed? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        package = create_draft_package()
        print("\nPackage object created. Review before running .run() method")
    else:
        print("Cancelled. Run script again when ready.")
