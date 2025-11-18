#!/usr/bin/env python3
"""
Detailed analysis of collection completeness
"""

import sys
import os
import json
import re
from collections import defaultdict
from pypubpub import Pubshelper_v6

# Get credentials from environment variables
email = os.environ.get('UNJOURNAL_EMAIL')
password = os.environ.get('UNJOURNAL_PASSWORD')

if not email or not password:
    print("ERROR: Please set UNJOURNAL_EMAIL and UNJOURNAL_PASSWORD environment variables")
    sys.exit(1)

community_url = os.environ.get('UNJOURNAL_URL', "https://unjournal.pubpub.org")
community_id = os.environ.get('UNJOURNAL_COMMUNITY_ID', "d28e8e57-7f59-486b-9395-b548158a27d6")

def get_all_collections(pubhelper):
    """Get all collections"""
    response = pubhelper.authed_request('collections', 'GET')
    return response

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

def extract_paper_title_from_eval_summary(title):
    """Extract paper title from evaluation summary title"""
    # Remove common prefixes
    patterns = [
        r'^Evaluation summary of ["\'](.+?)["\']',
        r'^Evaluation summary: ["\'](.+?)["\']',
        r'^Evaluation summary of (.+)',
        r'^Evaluation summary: (.+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('"').strip("'")

    return None

def find_related_evaluations(paper_title, all_pubs):
    """Find individual evaluations for a paper"""
    paper_title_lower = paper_title.lower()
    related = []

    for pub in all_pubs:
        title = pub.get('title', '').lower()

        # Check if this is an individual evaluation
        if not (title.startswith('evaluation ') or title.startswith('eval ')):
            continue

        # Check if the paper title is in the evaluation title
        if paper_title_lower in title:
            related.append(pub)

    return related

def main():
    print("="*80)
    print("DETAILED COLLECTION ANALYSIS")
    print("="*80)

    pubhelper = Pubshelper_v6(
        community_url=community_url,
        community_id=community_id,
        email=email,
        password=password
    )

    print("\nLogging in...")
    pubhelper.login()

    # Get all collections
    print("Fetching collections...")
    collections = get_all_collections(pubhelper)

    # Build collection map
    collection_map = {}
    for coll in collections:
        coll_id = coll['id']
        coll_slug = coll['slug']
        coll_title = coll['title']

        pubs = get_pubs_in_collection(pubhelper, coll_id)

        collection_map[coll_id] = {
            'id': coll_id,
            'slug': coll_slug,
            'title': coll_title,
            'kind': coll.get('kind'),
            'is_public': coll.get('isPublic'),
            'pubs': pubs,
            'pub_ids': set(pub['id'] for pub in pubs)
        }

        print(f"  [{coll_slug}] {len(pubs)} pubs")

    # Build pub map with collection memberships
    pub_map = {}
    for coll_id, coll_data in collection_map.items():
        for pub in coll_data['pubs']:
            if pub['id'] not in pub_map:
                pub_map[pub['id']] = {
                    'pub': pub,
                    'collections': []
                }
            pub_map[pub['id']]['collections'].append({
                'id': coll_id,
                'slug': coll_data['slug'],
                'title': coll_data['title']
            })

    # Identify thematic collections (excluding special ones)
    thematic_collections = {
        coll_id: coll_data
        for coll_id, coll_data in collection_map.items()
        if coll_data['slug'] not in [
            'commended-evaluations',
            'prize-winning-evaluations',
            'evaluation-summary-and-metrics',
            'templates-applied-and-policy-stream',
            'completed-uj-evaluation-packages'
        ]
    }

    print(f"\n\nFound {len(thematic_collections)} thematic collections")

    # Analysis: Check evaluation packages
    issues = []

    print("\n" + "="*80)
    print("CHECKING EVALUATION PACKAGE COMPLETENESS")
    print("="*80)

    # Find all evaluation summaries
    eval_summaries = []
    for pub_id, pub_data in pub_map.items():
        title = pub_data['pub'].get('title', '')
        if 'evaluation summary' in title.lower():
            eval_summaries.append(pub_data)

    print(f"\nFound {len(eval_summaries)} evaluation summaries")

    for summary_data in eval_summaries:
        summary_pub = summary_data['pub']
        summary_title = summary_pub.get('title', '')
        summary_slug = summary_pub.get('slug', '')
        summary_collections = summary_data['collections']

        # Extract paper title
        paper_title = extract_paper_title_from_eval_summary(summary_title)
        if not paper_title:
            continue

        # Find related individual evaluations
        all_pubs = [pd['pub'] for pd in pub_map.values()]
        related_evals = find_related_evaluations(paper_title, all_pubs)

        if not related_evals:
            # No individual evaluations found for this summary
            issues.append({
                'type': 'missing_individual_evaluations',
                'severity': 'high',
                'summary_title': summary_title,
                'summary_slug': summary_slug,
                'paper_title': paper_title,
                'message': f"Evaluation summary has no corresponding individual evaluations"
            })
            continue

        # Check if individual evaluations are in the same thematic collections
        summary_thematic_colls = set(
            c['slug'] for c in summary_collections
            if c['slug'] in [tc['slug'] for tc in thematic_collections.values()]
        )

        for eval_pub in related_evals:
            eval_id = eval_pub['id']
            eval_title = eval_pub.get('title', '')
            eval_slug = eval_pub.get('slug', '')
            eval_collections = pub_map[eval_id]['collections']

            eval_thematic_colls = set(
                c['slug'] for c in eval_collections
                if c['slug'] in [tc['slug'] for tc in thematic_collections.values()]
            )

            # Check if eval is missing from thematic collections that summary is in
            missing_collections = summary_thematic_colls - eval_thematic_colls

            if missing_collections:
                issues.append({
                    'type': 'eval_missing_from_thematic_collection',
                    'severity': 'medium',
                    'summary_title': summary_title,
                    'summary_slug': summary_slug,
                    'eval_title': eval_title,
                    'eval_slug': eval_slug,
                    'eval_id': eval_id,
                    'missing_from': list(missing_collections),
                    'message': f"Individual evaluation '{eval_title}' missing from thematic collections: {', '.join(missing_collections)}"
                })

            # Check if eval is in collections that summary is NOT in
            extra_collections = eval_thematic_colls - summary_thematic_colls

            if extra_collections:
                issues.append({
                    'type': 'eval_in_extra_collection',
                    'severity': 'low',
                    'summary_title': summary_title,
                    'summary_slug': summary_slug,
                    'eval_title': eval_title,
                    'eval_slug': eval_slug,
                    'eval_id': eval_id,
                    'extra_in': list(extra_collections),
                    'message': f"Individual evaluation '{eval_title}' is in extra thematic collections: {', '.join(extra_collections)}"
                })

    # Report issues
    print("\n" + "="*80)
    print("ISSUES FOUND")
    print("="*80)

    if not issues:
        print("\n✓ No issues found!")
    else:
        issues_by_severity = defaultdict(list)
        for issue in issues:
            issues_by_severity[issue['severity']].append(issue)

        total_issues = len(issues)
        print(f"\nFound {total_issues} potential issues:")

        for severity in ['high', 'medium', 'low']:
            severity_issues = issues_by_severity[severity]
            if not severity_issues:
                continue

            print(f"\n{severity.upper()} SEVERITY: {len(severity_issues)} issues")

            # Group by type
            issues_by_type = defaultdict(list)
            for issue in severity_issues:
                issues_by_type[issue['type']].append(issue)

            for issue_type, type_issues in issues_by_type.items():
                print(f"\n  {issue_type.replace('_', ' ').title()}: {len(type_issues)}")

                for i, issue in enumerate(type_issues[:5], 1):
                    print(f"\n    {i}. {issue['message']}")
                    if 'eval_slug' in issue:
                        print(f"       Eval slug: {issue['eval_slug']}")
                        print(f"       Eval ID: {issue['eval_id']}")
                    if 'missing_from' in issue:
                        print(f"       Collections: {', '.join(issue['missing_from'])}")

                if len(type_issues) > 5:
                    print(f"\n    ... and {len(type_issues) - 5} more")

    # Save detailed report
    report = {
        'issues': issues,
        'summary': {
            'total_issues': len(issues),
            'by_severity': {
                severity: len(issues_by_severity[severity])
                for severity in ['high', 'medium', 'low']
            },
            'by_type': {}
        },
        'recommendations': []
    }

    # Generate recommendations
    for issue in issues:
        if issue['type'] == 'eval_missing_from_thematic_collection':
            report['recommendations'].append({
                'action': 'add_to_collection',
                'pub_id': issue['eval_id'],
                'pub_slug': issue['eval_slug'],
                'collection_slugs': issue['missing_from'],
                'reason': issue['message']
            })

    print(f"\n\nGenerated {len(report['recommendations'])} recommendations")

    report_file = 'detailed_collection_analysis.json'
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"✓ Detailed report saved to: {report_file}")

    pubhelper.logout()

if __name__ == '__main__':
    main()
