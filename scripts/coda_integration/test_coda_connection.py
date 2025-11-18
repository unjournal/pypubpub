"""
Test Coda API connection and show sample data

Run this after setup_coda.py to verify everything works
"""

import os
from dotenv import load_dotenv
from codaio import Coda, Document

# Load environment variables
load_dotenv()

CODA_API_KEY = os.getenv('CODA_API_KEY')
CODA_DOC_ID = os.getenv('CODA_DOC_ID')
CODA_TABLE_ID = os.getenv('CODA_TABLE_ID')

def test_connection():
    """Test the Coda connection and show sample data"""

    print("=" * 80)
    print("TESTING CODA CONNECTION")
    print("=" * 80)
    print()

    # Check for required env vars
    if not CODA_API_KEY:
        print("❌ CODA_API_KEY not found in .env file")
        print("   Run: python setup_coda.py")
        return False

    if not CODA_DOC_ID or not CODA_TABLE_ID:
        print("❌ CODA_DOC_ID or CODA_TABLE_ID not found in .env file")
        print("   Run: python setup_coda.py")
        return False

    try:
        # Connect to Coda
        print("Connecting to Coda...")
        coda = Coda(CODA_API_KEY)

        # Get document
        print(f"Opening document: {CODA_DOC_ID}")
        doc = Document(CODA_DOC_ID, coda=coda)

        # Get table
        print(f"Opening table: {CODA_TABLE_ID}")
        table = doc.get_table(CODA_TABLE_ID)

        # Get rows
        print("Fetching rows...")
        rows = list(table.rows())

        print()
        print("=" * 80)
        print("✅ CONNECTION SUCCESSFUL!")
        print("=" * 80)
        print()
        print(f"Document: {doc.name if hasattr(doc, 'name') else 'Unknown'}")
        print(f"Table: {table.name}")
        print(f"Total rows: {len(rows)}")
        print()

        if rows:
            # Show column names
            first_row = rows[0]
            columns = list(first_row.keys())

            print(f"Columns ({len(columns)} total):")
            for i, col in enumerate(columns, 1):
                print(f"  {i:2d}. {col}")

            print()
            print("=" * 80)
            print("SAMPLE DATA (First Row)")
            print("=" * 80)
            print()

            # Show sample data (non-sensitive fields only)
            safe_fields = [
                "Name of the paper or project",
                "Please provide a concise summary",
                "Midpoint rating (for \"overall assessment\")",
                "Lower bound 90% CI (for \"overall assessment\")",
                "Upper bound 90% CI (for \"overall assessment\")",
            ]

            for field in safe_fields:
                value = first_row.get(field)
                if value:
                    # Truncate long values
                    value_str = str(value)[:100]
                    if len(str(value)) > 100:
                        value_str += "..."
                    print(f"{field}:")
                    print(f"  {value_str}")
                    print()

            print("=" * 80)
            print("🔒 SENSITIVE DATA FIELDS (not shown here):")
            print("=" * 80)
            sensitive_fields = [
                "Would you like to be publicly identified",
                "salted hash code or pseudonym",
                "Confidential comments section"
            ]
            for field in sensitive_fields:
                if field in columns:
                    print(f"  ✓ {field}")
            print()
            print("These fields will be stored in evaluation_data/confidential/ (gitignored)")

        else:
            print("⚠️  No rows found in table")

        print()
        print("=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print()
        print("1. Fetch all evaluations:")
        print("   python fetch_from_coda.py")
        print()
        print("2. Fetch evaluations for specific paper:")
        print('   python fetch_from_coda.py "Adjusting for Scale-Use Heterogeneity"')
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("❌ CONNECTION FAILED")
        print("=" * 80)
        print()
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check your API key is correct")
        print("  2. Verify document and table IDs")
        print("  3. Make sure you have access to the document")
        print("  4. Run setup again: python setup_coda.py")
        print()

        import traceback
        print("Full error details:")
        traceback.print_exc()

        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)
