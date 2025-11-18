"""
Quick extraction of ratings from Prati's PDF evaluation form

For immediate use before Coda API is set up
This is a temporary solution - eventually use fetch_from_coda.py
"""

import re

# Manually extracted from the PDF page 1-2 based on what we can see
# You'll need to open the PDF and fill in the actual values

PRATI_DATA = {
    "name": "Alberto Prati",
    "pseudonym": "Prati",
    "identified": True,  # Based on form indicating his name
    "paper_title": "Adjusting for Scale-Use Heterogeneity in Self-Reported Well-Being",

    # These are visible in the PDF screenshot you showed
    "ratings": {
        "overall_assessment": {
            "lower": 90,
            "mid": 95,
            "upper": 100
        },

        # TODO: Fill these in from the actual PDF
        # Look at the sliders/values in the form for each criterion

        "claims_evidence": {
            "lower": None,  # TODO: Check PDF
            "mid": None,
            "upper": None
        },

        "methods": {
            "lower": None,
            "mid": None,
            "upper": None
        },

        "advancing_knowledge": {
            "lower": None,
            "mid": None,
            "upper": None
        },

        "logic_communication": {
            "lower": None,
            "mid": None,
            "upper": None
        },

        "open_replicable": {
            "lower": None,
            "mid": None,
            "upper": None
        },

        "relevance_global": {
            "lower": None,
            "mid": None,
            "upper": None
        },

        # Journal tiers - remember to divide by 10!
        "journal_merit": {
            "lower": None,  # Value from PDF ÷ 10
            "mid": None,
            "upper": None
        },

        "journal_prediction": {
            "lower": None,
            "mid": None,
            "upper": None
        }
    },

    "summary": "",  # From "concise summary" field in PDF

    "evaluation_file": "See attached files",  # Check if there's a separate doc

    "field_expertise": "",  # From survey section at end
    "years_in_field": "",
    "reviews_completed": "",
    "time_spent": ""
}


def print_extraction_checklist():
    """Print a checklist for manual PDF extraction"""

    print("=" * 80)
    print("PRATI PDF EXTRACTION CHECKLIST")
    print("=" * 80)
    print()
    print("PDF: /Users/yosemite/Downloads/prati_The Unjournal Hub...")
    print()
    print("Page 1:")
    print("  [ ] Overall assessment - Lower, Mid, Upper (DONE: 90, 95, 100)")
    print()
    print("Page 2:")
    print("  [ ] Claims, evidence - Lower, Mid, Upper")
    print("  [ ] Methods - Lower, Mid, Upper")
    print("  [ ] Advancing knowledge - Lower, Mid, Upper")
    print()
    print("Page 3:")
    print("  [ ] Logic & communication - Lower, Mid, Upper")
    print("  [ ] Open, replicable - Lower, Mid, Upper")
    print("  [ ] Relevance to global priorities - Lower, Mid, Upper (may be blank)")
    print()
    print("Page 4:")
    print("  [ ] Journal tier (merit) - Lower, Mid, Upper (DIVIDE BY 10!)")
    print("  [ ] Journal tier (prediction) - Lower, Mid, Upper (DIVIDE BY 10!)")
    print()
    print("Comments:")
    print("  [ ] Extract any text comments below each rating slider")
    print()
    print("Evaluation Summary:")
    print("  [ ] 'Please provide a concise summary' text box")
    print()
    print("Attached Evaluation:")
    print("  [ ] Check if there's a separate doc/file linked or attached")
    print("  [ ] If not, Prati may have only filled the form")
    print()
    print("Survey (at end):")
    print("  [ ] Field/expertise")
    print("  [ ] Years in field")
    print("  [ ] Reviews completed")
    print("  [ ] Time spent")
    print()
    print("=" * 80)
    print()
    print("After extraction, update PRATI_DATA dictionary above and run:")
    print("  python extract_pdf_ratings.py > prati_ratings.json")
    print("=" * 80)


def export_for_pubpub():
    """Export in format ready for create_eval_scale_use.py"""

    # Check if data is complete
    missing = []
    for criterion, values in PRATI_DATA["ratings"].items():
        if values.get("mid") is None:
            missing.append(criterion)

    if missing:
        print("⚠️  WARNING: Missing ratings for:")
        for m in missing:
            print(f"   - {m}")
        print()
        print("Fill these in from the PDF before using this data")
        print()

    # Export as Python dict format
    print("# Copy this into create_eval_scale_use.py")
    print()
    print('"prati": {')
    for key, value in PRATI_DATA.items():
        if key == "ratings":
            print(f'    "ratings": {{')
            for rkey, rvalue in value.items():
                print(f'        "{rkey}": {rvalue},')
            print('    },')
        else:
            if isinstance(value, str):
                print(f'    "{key}": "{value}",')
            else:
                print(f'    "{key}": {value},')
    print('}')


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        export_for_pubpub()
    else:
        print_extraction_checklist()
        print()
        print("To export the data, run:")
        print("  python extract_pdf_ratings.py --export")
