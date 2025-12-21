#!/usr/bin/env python3
"""
Generate RePEc RDF files from unjournal.pubpub.org and deploy to Linode server

This script:
1. Connects to unjournal.pubpub.org
2. Generates fresh RePEc RDF metadata files
3. Uploads them to the Linode server for RePEc indexing
4. Triggers Google Scholar to pick up the new records

Usage:
    python scripts/generate_and_deploy_repec.py [--dry-run] [--skip-deploy]
"""

import os
import sys
import argparse
from datetime import datetime
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypubpub import Pubshelper_v6
from pypubpub.repec import RePEcPopulator


def get_credentials():
    """Get PubPub credentials from environment or config file"""
    try:
        # Try importing from tests/conf_settings.py
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests'))
        import conf_settings
        return {
            'community_url': conf_settings.community_url,
            'community_id': conf_settings.community_id,
            'email': conf_settings.email,
            'password': conf_settings.password
        }
    except ImportError:
        # Fall back to environment variables
        return {
            'community_url': os.environ.get('PUBPUB_COMMUNITY_URL', 'https://unjournal.pubpub.org'),
            'community_id': os.environ.get('PUBPUB_COMMUNITY_ID'),
            'email': os.environ.get('PUBPUB_EMAIL'),
            'password': os.environ.get('PUBPUB_PASSWORD')
        }


def generate_repec_files(output_dir='./repec_rdfs', dry_run=False):
    """
    Generate RePEc RDF files for all published evaluations

    Args:
        output_dir: Directory to write RDF files
        dry_run: If True, don't actually write files

    Returns:
        Path to generated RDF file
    """
    print("🔧 Setting up PubPub connection...")

    credentials = get_credentials()

    # Verify we have credentials
    if not all([credentials['community_url'], credentials['community_id']]):
        raise ValueError("Missing PubPub credentials. Set environment variables or create tests/conf_settings.py")

    # Create PubPub helper (login only needed for unpublished pubs)
    pub_helper = Pubshelper_v6(
        community_url=credentials['community_url'],
        community_id=credentials['community_id'],
        email=credentials.get('email'),
        password=credentials.get('password')
    )

    # Login if credentials provided (not strictly needed for public pubs)
    if credentials.get('email') and credentials.get('password'):
        print("🔐 Logging in to PubPub...")
        pub_helper.login()

    print(f"📚 Fetching pubs from {credentials['community_url']}...")

    # Create RePEc populator
    repec_helper = RePEcPopulator(
        pubhelper=pub_helper,
        inputdir=output_dir,
        outputdir=output_dir
    )

    if dry_run:
        print("🔍 DRY RUN - Would generate RePEc files but not writing...")
        return None

    print("📝 Generating RePEc RDF metadata...")
    metadata = repec_helper.build_metadata_file()

    # Find the generated file (most recent evalX_*.rdf)
    import glob
    rdf_files = glob.glob(f"{output_dir}/evalX_*.rdf")
    if not rdf_files:
        raise FileNotFoundError(f"No RDF files generated in {output_dir}")

    latest_rdf = max(rdf_files, key=os.path.getmtime)

    print(f"✅ Generated {len(metadata)} records")
    print(f"📄 RDF file: {latest_rdf}")

    # Get file size
    file_size = os.path.getsize(latest_rdf)
    print(f"📦 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    return latest_rdf


def deploy_to_linode(rdf_file, server='45.56.106.79', remote_path='/var/lib/repec/rdf/',
                     user='root', dry_run=False):
    """
    Deploy RDF file to Linode server via SCP

    Args:
        rdf_file: Path to local RDF file
        server: Linode server IP or hostname
        remote_path: Remote directory path on server
        user: SSH user
        dry_run: If True, show commands but don't execute

    Returns:
        True if successful, False otherwise
    """
    print(f"\n🚀 Deploying to Linode server {server}...")

    # Create standardized filename with current date
    timestamp = datetime.now().strftime('%Y%m%d')
    remote_filename = f"unjournal_eval_{timestamp}.rdf"
    remote_full_path = f"{remote_path}{remote_filename}"

    # SCP command
    scp_cmd = [
        'scp',
        rdf_file,
        f"{user}@{server}:{remote_full_path}"
    ]

    if dry_run:
        print(f"🔍 DRY RUN - Would execute:")
        print(f"  {' '.join(scp_cmd)}")
        return True

    print(f"📤 Uploading {os.path.basename(rdf_file)} to {user}@{server}:{remote_full_path}...")

    try:
        result = subprocess.run(scp_cmd, check=True, capture_output=True, text=True)
        print(f"✅ Successfully uploaded to {server}")

        # Also create a symlink to 'latest.rdf' on the server
        print("🔗 Creating symlink to latest.rdf...")
        ssh_cmd = [
            'ssh',
            f"{user}@{server}",
            f"cd {remote_path} && ln -sf {remote_filename} latest.rdf"
        ]
        subprocess.run(ssh_cmd, check=True, capture_output=True, text=True)
        print("✅ Symlink created")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Error deploying to server: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def trigger_repec_update(server='45.56.106.79', user='root', dry_run=False):
    """
    Trigger RePEc to re-index the files

    This is typically done by:
    1. Ensuring files are in the correct RePEc archive directory structure
    2. Notifying RePEc.org of the update (if automated)

    Args:
        server: Linode server IP
        user: SSH user
        dry_run: If True, show commands but don't execute
    """
    print("\n🔄 Triggering RePEc update...")

    if dry_run:
        print("🔍 DRY RUN - Would trigger RePEc update")
        print("ℹ️  Manual steps:")
        print("   1. Verify files are in RePEc archive structure")
        print("   2. Update RePEc last-modified timestamp")
        print("   3. Wait for RePEc crawler (runs periodically)")
        return

    # Check if there's a RePEc update script on the server
    ssh_cmd = [
        'ssh',
        f"{user}@{server}",
        "test -f /usr/local/bin/repec-update.sh && echo 'EXISTS' || echo 'NOT_FOUND'"
    ]

    try:
        result = subprocess.run(ssh_cmd, check=True, capture_output=True, text=True)
        if 'EXISTS' in result.stdout:
            print("📜 Found repec-update.sh script, running...")
            update_cmd = [
                'ssh',
                f"{user}@{server}",
                "/usr/local/bin/repec-update.sh"
            ]
            subprocess.run(update_cmd, check=True)
            print("✅ RePEc update script executed")
        else:
            print("ℹ️  No automatic update script found")
            print("📋 Manual steps to complete:")
            print("   1. Verify RDF files are in RePEc archive directory")
            print("   2. Update last-modified timestamp if needed")
            print("   3. RePEc will crawl periodically (usually within 24 hours)")
            print("   4. Google Scholar will index after RePEc processes the files")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not trigger automatic update: {e}")
        print("📋 Complete manually on the server")


def main():
    parser = argparse.ArgumentParser(
        description='Generate and deploy RePEc RDF files for The Unjournal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate and deploy to Linode
  python scripts/generate_and_deploy_repec.py

  # Generate only, don't deploy
  python scripts/generate_and_deploy_repec.py --skip-deploy

  # Dry run to see what would happen
  python scripts/generate_and_deploy_repec.py --dry-run

  # Custom server details
  python scripts/generate_and_deploy_repec.py --server my.server.com --user repec
        """
    )

    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually doing it')
    parser.add_argument('--skip-deploy', action='store_true',
                       help='Generate RDF files but do not deploy to server')
    parser.add_argument('--output-dir', default='./repec_rdfs',
                       help='Directory for RDF files (default: ./repec_rdfs)')
    parser.add_argument('--server', default='45.56.106.79',
                       help='Linode server address (default: 45.56.106.79)')
    parser.add_argument('--user', default='root',
                       help='SSH user (default: root)')
    parser.add_argument('--remote-path', default='/var/lib/repec/rdf/',
                       help='Remote path on server (default: /var/lib/repec/rdf/)')

    args = parser.parse_args()

    print("=" * 70)
    print("📚 RePEc RDF Generator and Deployer for The Unjournal")
    print("=" * 70)

    try:
        # Step 1: Generate RDF files
        rdf_file = generate_repec_files(
            output_dir=args.output_dir,
            dry_run=args.dry_run
        )

        if args.skip_deploy:
            print("\n✅ RDF generation complete (deployment skipped)")
            return 0

        if not rdf_file and not args.dry_run:
            print("❌ No RDF file generated")
            return 1

        # Step 2: Deploy to Linode
        if rdf_file or args.dry_run:
            success = deploy_to_linode(
                rdf_file if rdf_file else 'repec_rdfs/evalX_HHMMSS.rdf',
                server=args.server,
                remote_path=args.remote_path,
                user=args.user,
                dry_run=args.dry_run
            )

            if not success and not args.dry_run:
                print("❌ Deployment failed")
                return 1

        # Step 3: Trigger RePEc update
        trigger_repec_update(
            server=args.server,
            user=args.user,
            dry_run=args.dry_run
        )

        print("\n" + "=" * 70)
        print("✅ Complete!")
        print("=" * 70)
        print("\n📋 Next steps:")
        print("   1. Verify files on server: ssh {args.user}@{args.server}")
        print("   2. RePEc will crawl and index (usually within 24 hours)")
        print("   3. Google Scholar will pick up changes after RePEc processes them")
        print("   4. Check RePEc: https://ideas.repec.org/s/bjn/evalua.html")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
