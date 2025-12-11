#!/usr/bin/env python3
"""
Quick check to verify .env file is configured correctly
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to load .env from repo root
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root))

try:
    from dotenv import load_dotenv
    load_dotenv(repo_root / '.env')
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Continuing without .env file loading...")

def check_env():
    """Check if required environment variables are set."""

    print("\n" + "="*60)
    print("Coda API Configuration Check")
    print("="*60 + "\n")

    # Check each required variable
    checks = {
        'CODA_API_KEY': 'Coda API token',
        'CODA_DOC_ID': 'Coda document ID',
        'CODA_TABLE_ID': 'Coda table ID'
    }

    all_set = True

    for var_name, description in checks.items():
        value = os.getenv(var_name)

        if value and value != f"YOUR_{var_name[5:]}_HERE":
            # Value is set and not placeholder
            masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var_name}: {masked_value}")
        elif value:
            # Placeholder value
            print(f"⚠️  {var_name}: Still has placeholder value")
            print(f"   → Update in .env file")
            all_set = False
        else:
            # Not set
            print(f"❌ {var_name}: Not set")
            print(f"   → Add to .env file")
            all_set = False

    print("\n" + "="*60)

    if all_set:
        print("✅ All configuration looks good!")
        print("\nNext steps:")
        print("  1. Test connection: python test_coda_connection.py")
        print("  2. Fetch data: python fetch_from_coda.py")
    else:
        print("⚠️  Configuration incomplete")
        print("\nTo fix:")
        print("  1. Edit .env file in repository root")
        print("  2. Replace placeholder values with actual credentials")
        print("  3. See docs/CODA_SETUP.md for help finding these values")
        print("  4. Run this script again to verify")

    print("="*60 + "\n")

    # Check .env file exists
    env_file = repo_root / '.env'
    if not env_file.exists():
        print("\n⚠️  WARNING: .env file not found!")
        print(f"   Expected location: {env_file}")
        print("   Create one based on .env.example")

    return all_set


if __name__ == '__main__':
    success = check_env()
    sys.exit(0 if success else 1)
