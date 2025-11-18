"""
Interactive setup script for Coda API access

This will help you:
1. Get your Coda API key
2. Find your document and table IDs
3. Test the connection
4. Create the .env file
"""

import os
import sys
from codaio import Coda

def get_api_key():
    """Guide user to get API key"""
    print("=" * 80)
    print("STEP 1: Get Your Coda API Key")
    print("=" * 80)
    print()
    print("1. Go to: https://coda.io/account")
    print("2. Scroll down to 'API SETTINGS'")
    print("3. Click 'Generate API Token'")
    print("4. Give it a name like 'Unjournal PubPub Automation'")
    print("5. Copy the token (it will only be shown once!)")
    print()

    api_key = input("Paste your API key here: ").strip()

    if not api_key or len(api_key) < 30:
        print("❌ That doesn't look like a valid API key. Please try again.")
        sys.exit(1)

    return api_key

def test_connection(api_key):
    """Test the API connection and list docs"""
    print()
    print("=" * 80)
    print("STEP 2: Test Connection and Find Your Document")
    print("=" * 80)
    print()
    print("Testing connection...")

    try:
        coda = Coda(api_key)
        docs = list(coda.list_docs())

        print(f"✅ Connection successful! Found {len(docs)} documents.")
        print()

        if not docs:
            print("⚠️  No documents found. Make sure you have access to the Unjournal Coda doc.")
            return None, None

        # Show available documents
        print("Available documents:")
        for i, doc in enumerate(docs, 1):
            print(f"\n{i}. {doc.name}")
            print(f"   ID: {doc.id}")
            print(f"   URL: {doc.href}")

        print()

        # Let user select document
        if len(docs) == 1:
            selected_doc = docs[0]
            print(f"Using the only available document: {selected_doc.name}")
        else:
            while True:
                try:
                    choice = input(f"\nWhich document contains the evaluations? (1-{len(docs)}): ").strip()
                    idx = int(choice) - 1
                    if 0 <= idx < len(docs):
                        selected_doc = docs[idx]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(docs)}")
                except (ValueError, IndexError):
                    print(f"Please enter a number between 1 and {len(docs)}")

        return selected_doc, coda

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def find_table(doc, coda):
    """Find the evaluations table"""
    print()
    print("=" * 80)
    print("STEP 3: Find the Evaluations Table")
    print("=" * 80)
    print()

    try:
        tables = list(doc.list_tables())

        print(f"Found {len(tables)} tables in '{doc.name}':")
        print()

        for i, table in enumerate(tables, 1):
            print(f"{i}. {table.name}")
            print(f"   ID: {table.id}")
            print(f"   Rows: {table.row_count if hasattr(table, 'row_count') else 'unknown'}")
            print()

        # Let user select table
        while True:
            try:
                choice = input(f"Which table contains the evaluations? (1-{len(tables)}): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(tables):
                    selected_table = tables[idx]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(tables)}")
            except (ValueError, IndexError):
                print(f"Please enter a number between 1 and {len(tables)}")

        return selected_table

    except Exception as e:
        print(f"❌ Error listing tables: {e}")
        return None

def preview_table(table):
    """Show a preview of the table data"""
    print()
    print("=" * 80)
    print("STEP 4: Preview Table Data")
    print("=" * 80)
    print()

    try:
        rows = list(table.rows())[:3]  # Get first 3 rows

        if not rows:
            print("⚠️  Table appears to be empty")
            return

        print(f"Preview of first {len(rows)} row(s):")
        print()

        # Get column names from first row
        first_row = rows[0]
        columns = list(first_row.keys())

        print("Columns found:")
        for col in columns[:10]:  # Show first 10 columns
            print(f"  - {col}")

        if len(columns) > 10:
            print(f"  ... and {len(columns) - 10} more")

        print()
        print("Sample data from first row:")
        for col in columns[:5]:  # Show first 5 columns with data
            value = first_row.get(col)
            if value:
                value_str = str(value)[:50]  # Truncate long values
                print(f"  {col}: {value_str}")

        print()
        print("✅ Table looks good!")

    except Exception as e:
        print(f"❌ Error previewing table: {e}")

def create_env_file(api_key, doc_id, table_id):
    """Create .env file with credentials"""
    print()
    print("=" * 80)
    print("STEP 5: Create .env File")
    print("=" * 80)
    print()

    env_content = f"""# Coda API Configuration
# Generated by setup_coda.py
# NEVER commit this file to git!

CODA_API_KEY={api_key}
CODA_DOC_ID={doc_id}
CODA_TABLE_ID={table_id}

# PubPub Configuration (from conf.py)
PUBPUB_EMAIL=contact@unjournal.org
PUBPUB_PASSWORD=rap5nje8VWR!khd1cjz
PUBPUB_COMMUNITY_ID=d28e8e57-7f59-486b-9395-b548158a27d6
PUBPUB_COMMUNITY_URL=https://unjournal.pubpub.org
"""

    env_path = ".env"

    if os.path.exists(env_path):
        response = input(f"\n⚠️  {env_path} already exists. Overwrite? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Setup cancelled. Your existing .env file was not modified.")
            return

    with open(env_path, 'w') as f:
        f.write(env_content)

    print(f"✅ Created {env_path}")
    print()
    print("⚠️  IMPORTANT: Never commit .env to git!")
    print("   It's already in .gitignore, but be careful.")

def main():
    """Main setup workflow"""
    print("""
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║                   CODA API SETUP FOR UNJOURNAL                           ║
    ║                                                                          ║
    ║  This script will help you connect to Coda and configure automation     ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Get API key
    api_key = get_api_key()

    # Step 2: Test connection and find document
    doc, coda = test_connection(api_key)
    if not doc:
        print("\n❌ Setup failed. Please check your API key and try again.")
        sys.exit(1)

    # Step 3: Find table
    table = find_table(doc, coda)
    if not table:
        print("\n❌ Setup failed. Could not find table.")
        sys.exit(1)

    # Step 4: Preview table
    preview_table(table)

    # Step 5: Create .env file
    create_env_file(api_key, doc.id, table.id)

    # Success!
    print()
    print("=" * 80)
    print("✅ SETUP COMPLETE!")
    print("=" * 80)
    print()
    print("Your Coda connection is configured. Next steps:")
    print()
    print("1. Test the connection:")
    print("   python test_coda_connection.py")
    print()
    print("2. Fetch evaluation data:")
    print('   python fetch_from_coda.py "Paper Title"')
    print()
    print("3. Or fetch all evaluations:")
    print("   python fetch_from_coda.py")
    print()
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
