"""
Fetch evaluation data from Coda.io tables for PubPub package creation

This script:
1. Connects to Coda API
2. Fetches evaluation data from the evaluations table
3. Separates sensitive data (pseudonyms, confidential comments)
4. Creates sanitized data structures for PubPub posting
5. Stores sensitive data in local gitignored files only

SECURITY NOTES:
- Requires CODA_API_KEY environment variable
- Sensitive data saved to evaluation_data/ directory (gitignored)
- Public scripts never contain pseudonyms or confidential comments
- Hash codes used to match evaluations without exposing identity
"""

import os
import json
import hashlib
from typing import Dict, List, Optional
from codaio import Coda, Document, Cell

# Configuration
CODA_DOC_ID = os.getenv('CODA_DOC_ID')  # Set this in your .env file
CODA_TABLE_ID = os.getenv('CODA_TABLE_ID')  # The evaluations table
CODA_API_KEY = os.getenv('CODA_API_KEY')  # Never commit this!

# Directories for data storage
SENSITIVE_DATA_DIR = "evaluation_data/confidential"
PUBLIC_DATA_DIR = "evaluation_data/public"


def create_hash_id(evaluator_name: str, paper_title: str) -> str:
    """
    Create a non-reversible hash to identify evaluations without exposing identity
    This matches the 'salted hash code' concept from the Coda form
    """
    combined = f"{evaluator_name}_{paper_title}_unjournal_salt_2024"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def fetch_evaluation_data(paper_title: str = None) -> List[Dict]:
    """
    Fetch evaluation data from Coda

    Args:
        paper_title: Optional filter for specific paper

    Returns:
        List of evaluation records
    """

    if not CODA_API_KEY:
        raise ValueError("CODA_API_KEY environment variable not set")

    coda = Coda(CODA_API_KEY)
    doc = Document(CODA_DOC_ID, coda=coda)
    table = doc.get_table(CODA_TABLE_ID)

    # Fetch all rows
    rows = table.rows()

    evaluations = []
    for row in rows:
        # Extract data from Coda row
        eval_data = {
            # Public fields
            "paper_title": row.get("Name of the paper or project"),
            "summary": row.get("Please provide a concise summary"),
            "evaluation_file": row.get("Upload your evaluation"),  # File attachment

            # Ratings (all public)
            "overall_assessment": {
                "lower": row.get("Lower bound 90% CI (Overall)"),
                "mid": row.get("Midpoint rating (Overall)"),
                "upper": row.get("Upper bound 90% CI (Overall)")
            },
            "claims_evidence": {
                "lower": row.get("Lower bound 90% CI (Claims)"),
                "mid": row.get("Midpoint rating (Claims)"),
                "upper": row.get("Upper bound 90% CI (Claims)")
            },
            # ... other ratings

            # Comments on ratings (public)
            "comments": {
                "overall": row.get("Comments on Overall assessment"),
                # ... other comments
            },

            # SENSITIVE - store separately
            "_sensitive": {
                "evaluator_name": row.get("Would you like to be publicly identified"),
                "pseudonym_or_hash": row.get("salted hash code or pseudonym"),
                "confidential_comments": row.get("Confidential comments section"),
                "wants_identification": row.get("Tick here if you would like to be identified"),
            },

            # Metadata
            "submission_date": row.get("Submission Date"),
            "evaluation_manager": row.get("Evaluation Manager")
        }

        # Filter by paper if specified
        if paper_title and eval_data["paper_title"] != paper_title:
            continue

        evaluations.append(eval_data)

    return evaluations


def separate_sensitive_data(evaluations: List[Dict]) -> tuple:
    """
    Separate sensitive data from public data

    Returns:
        (public_data, sensitive_data) tuple
    """

    public_evaluations = []
    sensitive_mapping = {}

    for eval_data in evaluations:
        # Create hash ID for this evaluation
        hash_id = create_hash_id(
            eval_data["_sensitive"]["evaluator_name"] or "anonymous",
            eval_data["paper_title"]
        )

        # Public data - use hash ID instead of real identity
        public_eval = {
            "hash_id": hash_id,
            "paper_title": eval_data["paper_title"],
            "summary": eval_data["summary"],
            "ratings": {
                "overall_assessment": eval_data["overall_assessment"],
                "claims_evidence": eval_data["claims_evidence"],
                # ... all public ratings
            },
            "comments": eval_data["comments"],
            "submission_date": eval_data["submission_date"]
        }

        # Sensitive data - stored separately, linked by hash_id
        sensitive_data = {
            "hash_id": hash_id,
            "evaluator_name": eval_data["_sensitive"]["evaluator_name"],
            "pseudonym": eval_data["_sensitive"]["pseudonym_or_hash"],
            "confidential_comments": eval_data["_sensitive"]["confidential_comments"],
            "wants_public_id": eval_data["_sensitive"]["wants_identification"],
        }

        public_evaluations.append(public_eval)
        sensitive_mapping[hash_id] = sensitive_data

    return public_evaluations, sensitive_mapping


def save_data(public_data: List[Dict], sensitive_data: Dict, paper_slug: str):
    """
    Save data to appropriate directories

    Args:
        public_data: Sanitized evaluation data (safe to commit)
        sensitive_data: Identity and confidential info (gitignored)
        paper_slug: URL-friendly paper identifier
    """

    # Create directories if needed
    os.makedirs(SENSITIVE_DATA_DIR, exist_ok=True)
    os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)

    # Save public data (can be committed to git)
    public_file = f"{PUBLIC_DATA_DIR}/{paper_slug}_evaluations.json"
    with open(public_file, 'w') as f:
        json.dump(public_data, f, indent=2)
    print(f"✅ Saved public data to: {public_file}")

    # Save sensitive data (NEVER commit - gitignored)
    sensitive_file = f"{SENSITIVE_DATA_DIR}/{paper_slug}_sensitive.json"
    with open(sensitive_file, 'w') as f:
        json.dump(sensitive_data, f, indent=2)
    print(f"🔒 Saved sensitive data to: {sensitive_file} (gitignored)")


def prepare_for_pubpub(public_data: List[Dict], sensitive_data: Dict) -> List[Dict]:
    """
    Prepare data structure for PubPub posting
    Uses public data during draft phase, merges with sensitive for final

    Args:
        public_data: Public evaluation data
        sensitive_data: Sensitive identity mapping

    Returns:
        List of evaluator dicts ready for PubPub EvaluationPackage
    """

    pubpub_evaluations = []

    for eval_data in public_data:
        hash_id = eval_data["hash_id"]
        sensitive = sensitive_data[hash_id]

        # For DRAFT packages: use pseudonym/hash, no real names
        draft_eval = {
            "pseudonym": sensitive["pseudonym"],
            "identified": False,  # Always false in draft
            "summary": eval_data["summary"],
            "ratings": eval_data["ratings"],
            "comments": eval_data["comments"],
        }

        # For FINAL packages: add real name if they want identification
        final_eval = dict(draft_eval)
        if sensitive["wants_public_id"]:
            final_eval["name"] = sensitive["evaluator_name"]
            final_eval["identified"] = True

        pubpub_evaluations.append({
            "draft": draft_eval,
            "final": final_eval,
            "hash_id": hash_id
        })

    return pubpub_evaluations


def main(paper_title: str = None):
    """
    Main workflow: Fetch from Coda, separate sensitive data, prepare for PubPub
    """

    print("=" * 80)
    print("FETCHING EVALUATION DATA FROM CODA")
    print("=" * 80)

    # Fetch data
    print(f"\nFetching evaluations for: {paper_title or 'all papers'}")
    evaluations = fetch_evaluation_data(paper_title)
    print(f"✅ Found {len(evaluations)} evaluations")

    # Separate sensitive data
    print("\nSeparating sensitive data...")
    public_data, sensitive_data = separate_sensitive_data(evaluations)

    # Save to files
    paper_slug = paper_title.lower().replace(" ", "_")[:50] if paper_title else "all"
    save_data(public_data, sensitive_data, paper_slug)

    # Prepare for PubPub
    print("\nPreparing data for PubPub...")
    pubpub_data = prepare_for_pubpub(public_data, sensitive_data)

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total evaluations: {len(pubpub_data)}")
    print(f"\nPublic data: {PUBLIC_DATA_DIR}/")
    print(f"Sensitive data: {SENSITIVE_DATA_DIR}/ (gitignored)")
    print("\nNext steps:")
    print("1. Review public data file (safe to share)")
    print("2. Use pubpub_data for creating evaluation packages")
    print("3. Use 'draft' version when sharing with authors")
    print("4. Use 'final' version after author response")
    print("=" * 80)

    return pubpub_data


if __name__ == "__main__":
    import sys

    # Check for API key
    if not os.getenv('CODA_API_KEY'):
        print("❌ Error: CODA_API_KEY environment variable not set")
        print("\nSet it in your .env file or export it:")
        print("  export CODA_API_KEY='your_key_here'")
        sys.exit(1)

    # Get paper title from command line if provided
    paper_title = sys.argv[1] if len(sys.argv) > 1 else None

    # Run main workflow
    data = main(paper_title)
