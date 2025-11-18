#!/usr/bin/env python3
"""
Audit all collections and identify missing or misplaced pubs
"""

import sys
import os
import json
from collections import defaultdict
from pypubpub import Pubshelper_v6

# Get credentials from environment variables
email = os.environ.get('UNJOURNAL_EMAIL')
password = os.environ.get('UNJOURNAL_PASSWORD')

if not email or not password:
    print("ERROR: Please set UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD environment variables")
    sys.exit(1)

# Use Unjournal defaults
community_url = os.environ.get('UNJOURNAL_URL', "https://unjournal.pubpub.org")
community_id = os.environ.get('UNJOURNAL_COMMUNITY_ID', "d28e8e57-7f59-486b-9395-b548158a27d6")

print(f"Using credentials: {email}, URL: {community_url}")

def get_all_collections(pubhelper):
    """Get all collections in the community"""
    try:
        # Query collections endpoint
        response = pubhelper.authed_request('collections', 'GET')
        return response
    except Exception as e:
        print(f"Error getting collections: {e}")
        return []

def get_pubs_in_collection(pubhelper, collection_id):
    """Get all pubs in a collection"""
    all_pubs = []
    offset = 0
    limit = 200

    while True:
        response = pubhelper.get_many_pubs(
            collection_ids=[collection_id],
            limit=limit,
            offset=offset,
            isReleased=None
        )

        pub_ids = response.get('pubIds', [])
        pubs_by_id = response.get('pubsById', {})

        if not pub_ids:
            break

        batch_pubs = [pubs_by_id[pub_id] for pub_id in pub_ids if pub_id in pubs_by_id]
        all_pubs.extend(batch_pubs)

        if response.get('loadedAllPubs', False) or len(pub_ids) < limit:
            break

        offset += limit

    return all_pubs

def analyze_pub_title(title):
    """Analyze a pub title to determine its type"""
    title_lower = title.lower()

    # Check for evaluation summaries
    if 'evaluation summary' in title_lower or 'eval summary' in title_lower:
        return 'evaluation_summary'

    # Check for individual evaluations
    if title_lower.startswith('evaluation ') or title_lower.startswith('eval '):
        return 'individual_evaluation'

    # Check for templates
    if 'template' in title_lower:
        return 'template'

    # Check for special types
    if any(word in title_lower for word in ['guide', 'handbook', 'process', 'faq']):
        return 'documentation'

    return 'other'

def main():
    print("="*80)
    print("AUDITING ALL COLLECTIONS")
    print("="*80)

    # Initialize and login
    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )

    print("\nLogging in...")
    pubhelper.login()
    print("✓ Logged in successfully")

    # Get all collections
    print("\nFetching all collections...")
    collections = get_all_collections(pubhelper)

    if isinstance(collections, list):
        print(f"✓ Found {len(collections)} collections")
    else:
        print(f"✓ Found collections (response type: {type(collections)})")
        # Try to extract collections from response
        if isinstance(collections, dict):
            collections = collections.get('collections', [])

    # Analyze each collection
    collection_data = {}
    all_pubs_by_id = {}

    print("\n" + "="*80)
    print("ANALYZING COLLECTIONS")
    print("="*80)

    for collection in collections:
        coll_id = collection.get('id')
        coll_title = collection.get('title', 'Untitled')
        coll_slug = collection.get('slug', 'no-slug')
        coll_kind = collection.get('kind', 'unknown')
        coll_is_public = collection.get('isPublic', False)

        print(f"\n[{coll_slug}] {coll_title}")
        print(f"  Kind: {coll_kind}, Public: {coll_is_public}")

        # Get pubs in this collection
        pubs = get_pubs_in_collection(pubhelper, coll_id)
        print(f"  Pubs: {len(pubs)}")

        # Store collection data
        collection_data[coll_id] = {
            'title': coll_title,
            'slug': coll_slug,
            'kind': coll_kind,
            'is_public': coll_is_public,
            'pub_count': len(pubs),
            'pubs': pubs,
            'pub_ids': [pub['id'] for pub in pubs]
        }

        # Track all pubs
        for pub in pubs:
            if pub['id'] not in all_pubs_by_id:
                all_pubs_by_id[pub['id']] = pub
                pub['_collections'] = []
            all_pubs_by_id[pub['id']]['_collections'].append({
                'id': coll_id,
                'title': coll_title,
                'slug': coll_slug
            })

    # Analyze patterns
    print("\n" + "="*80)
    print("PATTERN ANALYSIS")
    print("="*80)

    # Group pubs by type
    pubs_by_type = defaultdict(list)
    for pub_id, pub in all_pubs_by_id.items():
        pub_type = analyze_pub_title(pub.get('title', ''))
        pubs_by_type[pub_type].append(pub)

    print(f"\nPub type distribution:")
    for pub_type, pubs in sorted(pubs_by_type.items()):
        print(f"  {pub_type}: {len(pubs)}")

    # Find evaluation summaries and their related evaluations
    print("\n" + "="*80)
    print("EVALUATION PACKAGE ANALYSIS")
    print("="*80)

    eval_summaries = pubs_by_type['evaluation_summary']
    individual_evals = pubs_by_type['individual_evaluation']

    print(f"\nFound {len(eval_summaries)} evaluation summaries")
    print(f"Found {len(individual_evals)} individual evaluations")

    # Check for evaluation summaries without corresponding individual evaluations
    issues = []

    for summary in eval_summaries:
        summary_title = summary.get('title', '')
        summary_slug = summary.get('slug', '')

        # Extract paper title from summary
        paper_title = summary_title.replace('Evaluation summary of ', '').replace('"', '').strip()

        # Find related evaluations
        related_evals = [
            e for e in individual_evals
            if paper_title.lower() in e.get('title', '').lower()
        ]

        # Check if they're in the same collections
        summary_collections = set(c['slug'] for c in summary.get('_collections', []))

        for eval_pub in related_evals:
            eval_collections = set(c['slug'] for c in eval_pub.get('_collections', []))

            # Check for missing in collections
            missing_in_summary_colls = summary_collections - eval_collections
            missing_in_eval_colls = eval_collections - summary_collections

            if missing_in_summary_colls:
                issues.append({
                    'type': 'eval_missing_from_collections',
                    'summary': summary_title,
                    'summary_slug': summary_slug,
                    'eval': eval_pub.get('title'),
                    'eval_slug': eval_pub.get('slug'),
                    'eval_id': eval_pub.get('id'),
                    'missing_from': list(missing_in_summary_colls),
                    'severity': 'medium'
                })

    # Check for special collections
    special_collections = {
        'prize-winning-evaluations': 'Prize-winning evaluations',
        'commended-evaluations': 'Commended evaluations',
        'evaluation-summary-and-metrics': 'Evaluation Summary and Metrics'
    }

    print("\n" + "="*80)
    print("SPECIAL COLLECTIONS CHECK")
    print("="*80)

    for slug, name in special_collections.items():
        coll = next((c for c in collection_data.values() if c['slug'] == slug), None)
        if coll:
            print(f"\n{name} ({slug}): {coll['pub_count']} pubs")

            # Check for templates or documentation in these collections
            for pub_id in coll['pub_ids']:
                pub = all_pubs_by_id[pub_id]
                pub_type = analyze_pub_title(pub.get('title', ''))

                if pub_type in ['template', 'documentation']:
                    issues.append({
                        'type': 'wrong_pub_type_in_collection',
                        'collection': name,
                        'collection_slug': slug,
                        'pub_title': pub.get('title'),
                        'pub_slug': pub.get('slug'),
                        'pub_id': pub.get('id'),
                        'pub_type': pub_type,
                        'severity': 'low'
                    })

    # Generate report
    print("\n" + "="*80)
    print("ISSUES FOUND")
    print("="*80)

    if not issues:
        print("\n✓ No issues found!")
    else:
        print(f"\nFound {len(issues)} potential issues:")

        # Group by type
        issues_by_type = defaultdict(list)
        for issue in issues:
            issues_by_type[issue['type']].append(issue)

        for issue_type, issue_list in issues_by_type.items():
            print(f"\n{issue_type.replace('_', ' ').title()}: {len(issue_list)}")

            for i, issue in enumerate(issue_list[:10], 1):  # Show first 10
                if issue['type'] == 'eval_missing_from_collections':
                    print(f"\n  {i}. Evaluation not in same collections as summary:")
                    print(f"     Summary: {issue['summary']}")
                    print(f"     Eval: {issue['eval']}")
                    print(f"     Missing from: {', '.join(issue['missing_from'])}")
                elif issue['type'] == 'wrong_pub_type_in_collection':
                    print(f"\n  {i}. Unexpected pub type in collection:")
                    print(f"     Collection: {issue['collection']}")
                    print(f"     Pub: {issue['pub_title']}")
                    print(f"     Type: {issue['pub_type']}")

            if len(issue_list) > 10:
                print(f"\n  ... and {len(issue_list) - 10} more")

    # Save detailed report to JSON
    report_file = 'collection_audit_report.json'
    report = {
        'collections': {
            coll_id: {
                'title': data['title'],
                'slug': data['slug'],
                'kind': data['kind'],
                'is_public': data['is_public'],
                'pub_count': data['pub_count'],
                'pub_slugs': [pub.get('slug') for pub in data['pubs']]
            }
            for coll_id, data in collection_data.items()
        },
        'issues': issues,
        'stats': {
            'total_collections': len(collections),
            'total_unique_pubs': len(all_pubs_by_id),
            'pubs_by_type': {k: len(v) for k, v in pubs_by_type.items()}
        }
    }

    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n\n✓ Detailed report saved to: {report_file}")

    # Logout
    print("\nLogging out...")
    pubhelper.logout()
    print("✓ Done")

    return 0

if __name__ == '__main__':
    sys.exit(main())
