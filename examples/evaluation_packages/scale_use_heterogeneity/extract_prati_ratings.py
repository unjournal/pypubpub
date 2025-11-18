"""
Helper script to extract Alberto Prati's complete ratings from the evaluation form PDF

This is a manual extraction guide - review the PDF and fill in the ratings below.
Once complete, copy this data into create_eval_scale_use.py
"""

# Based on the evaluation form structure, Prati should have these ratings:

prati_ratings_template = {
    "name": "Alberto Prati",
    "pseudonym": "Prati",
    "identified": True,  # Confirm this from the form
    "summary": "",  # Extract from "Please provide a concise summary" field
    "review_file": None,  # Path if separate document exists

    "ratings": {
        # Percentile ratings (0-100 scale)
        "overall_assessment": {
            "lower": 90,  # ✓ CONFIRMED from PDF
            "mid": 95,     # ✓ CONFIRMED from PDF
            "upper": 100   # ✓ CONFIRMED from PDF
        },

        "claims_evidence": {
            "lower": None,  # TODO: Extract from PDF
            "mid": None,
            "upper": None
        },

        "methods": {
            "lower": None,  # TODO: Extract from PDF
            "mid": None,
            "upper": None
        },

        "advancing_knowledge": {
            "lower": None,  # TODO: Extract from PDF
            "mid": None,
            "upper": None
        },

        "logic_communication": {
            "lower": None,  # TODO: Extract from PDF
            "mid": None,
            "upper": None
        },

        "open_replicable": {
            "lower": None,  # TODO: Extract from PDF
            "mid": None,
            "upper": None
        },

        "relevance_global": {
            "lower": None,  # TODO: Extract from PDF (may be 0 if not applicable)
            "mid": None,
            "upper": None
        },

        # Journal tier ratings (0-5.0 scale, but PDF shows 0-50, divide by 10)
        "journal_merit": {
            "lower": None,  # TODO: Extract from PDF and divide by 10
            "mid": None,
            "upper": None
        },

        "journal_prediction": {
            "lower": None,  # TODO: Extract from PDF and divide by 10
            "mid": None,
            "upper": None
        }
    },

    "comments": {
        # Extract any comments on specific ratings
        "overall": "",
        "claims_evidence": "",
        "methods": "",
        "advancing_knowledge": "",
        "logic_communication": "",
        "open_replicable": "",
        "relevance_global": "",
        "journal_tiers": ""
    },

    "claim_assessment": {
        # From "Claim identification, assessment, & implications" section
        "main_claim": "",  # TODO: Extract if provided
        "belief_in_claim": "",  # TODO: Extract if provided
        "additional_evidence_needed": "",  # TODO: Extract if provided
        "implications": ""  # TODO: Extract if provided
    },

    "evaluator_details": {
        "field_expertise": "",  # TODO: Extract from survey section
        "years_in_field": "",  # TODO: Extract
        "reviews_completed": "",  # TODO: Extract
        "time_spent": "",  # TODO: Extract
        "willing_to_review_revision": "",  # TODO: Extract
        "interested_in_joint_report": ""  # TODO: Extract
    }
}

def print_extraction_guide():
    """Print a guide for manual extraction"""
    print("=" * 80)
    print("PRATI RATINGS EXTRACTION GUIDE")
    print("=" * 80)
    print()
    print("PDF Location: /Users/yosemite/Downloads/prati_The Unjournal Hub...")
    print()
    print("Please open the PDF and extract the following data:")
    print()
    print("1. OVERALL ASSESSMENT (Page 1-2)")
    print("   ✓ Already extracted: Lower=90, Mid=95, Upper=100")
    print()
    print("2. CLAIMS, STRENGTH AND CHARACTERIZATION OF EVIDENCE")
    print("   Look for sliders/values for Lower, Midpoint, Upper CI")
    print()
    print("3. METHODS: JUSTIFICATION, REASONABLENESS, VALIDITY")
    print("   Look for sliders/values for Lower, Midpoint, Upper CI")
    print()
    print("4. ADVANCING KNOWLEDGE AND PRACTICE")
    print("   Look for sliders/values for Lower, Midpoint, Upper CI")
    print()
    print("5. LOGIC & COMMUNICATION")
    print("   Look for sliders/values for Lower, Midpoint, Upper CI")
    print()
    print("6. OPEN, COLLABORATIVE, REPLICABLE")
    print("   Look for sliders/values for Lower, Midpoint, Upper CI")
    print()
    print("7. RELEVANCE TO GLOBAL PRIORITIES")
    print("   Look for sliders/values (may be blank/0)")
    print()
    print("8. JOURNAL RANKING TIERS")
    print("   Two sets of values (merit and prediction)")
    print("   IMPORTANT: Divide by 10 (they're on 0-50 scale, we need 0-5.0)")
    print()
    print("9. COMMENTS")
    print("   Extract any text comments below each rating")
    print()
    print("10. CLAIM ASSESSMENT (if filled)")
    print("    Main claim identified")
    print("    Belief in claim")
    print("    Additional evidence needed")
    print()
    print("11. EVALUATOR DETAILS (at end)")
    print("    Field/expertise")
    print("    Years in field")
    print("    Number of reviews completed")
    print("    Time spent on evaluation")
    print()
    print("=" * 80)
    print("After extraction, update the prati_ratings_template dictionary above")
    print("and copy it into create_eval_scale_use.py")
    print("=" * 80)

def validate_ratings(ratings):
    """Check if ratings are complete and valid"""
    issues = []

    for criterion, values in ratings["ratings"].items():
        if values.get("mid") is None:
            issues.append(f"Missing midpoint for {criterion}")
        if values.get("lower") is None:
            issues.append(f"Missing lower CI for {criterion}")
        if values.get("upper") is None:
            issues.append(f"Missing upper CI for {criterion}")

        # Validate ranges
        if all(v is not None for v in values.values()):
            if not (values["lower"] <= values["mid"] <= values["upper"]):
                issues.append(f"Invalid range for {criterion}: {values}")

    return issues

if __name__ == "__main__":
    print_extraction_guide()

    print("\nCurrent template status:")
    issues = validate_ratings(prati_ratings_template)

    if issues:
        print(f"\n⚠️  Found {len(issues)} missing/invalid fields:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("\n✅ All ratings complete and valid!")

    print("\n" + "=" * 80)
    print("NOTE: You'll also need to find/request Prati's written evaluation text")
    print("Check if there's a separate document, or if only form ratings were provided")
    print("=" * 80)
