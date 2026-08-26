#!/usr/bin/env python3
"""
Validate a generated RePEc ReDIF file before it is deployed.

Blocking checks (exit code 1):
  1. Duplicate handles within the new file
  2. Handles that already appear in previously deployed .rdf files
  3. Template / blacklisted entries that slipped through
  4. Records missing a required field

Warnings (exit code 0, but reported):
  handle format, number format, empty/placeholder abstracts, missing DOI

Usage:
    python scripts/validate_repec_rdf.py <new_file.rdf> [existing_rdf_dir]
"""

import glob
import os
import re
import sys

REQUIRED_FIELDS = ['Template-Type', 'Title', 'Handle', 'Creation-Date', 'File-URL']

HANDLE_RE = re.compile(r'^RePEc:bjn:evalua:[A-Za-z0-9._-]+$')
NUMBER_RE = re.compile(r'^\d{4}-\d{2}$')

# Slugs that must never be published, matched exactly against the handle tail.
BLACKLIST_SLUGS = {'templatesummary', 'evalsummary', 'template-pub'}
# Substrings that must never appear in a title or handle (case-insensitive).
BLACKLIST_SUBSTRINGS = ['[template]', 'templatesummary', 'template-pub']
BLACKLIST_TITLE_RE = re.compile(r'(?i)\[template')

# An abstract that is only a bare prefix carries no information.
PLACEHOLDER_ABSTRACTS = {'evaluation summary and metrics:', 'evaluation of "', 'none', ''}


def parse_records(text):
    """Split a ReDIF file into records. A record runs from a 'Template-Type:'
    line up to the line before the next 'Template-Type:' (or EOF)."""
    records = []
    current = None
    for line in text.splitlines():
        if line.startswith('Template-Type:'):
            if current is not None:
                records.append(current)
            current = []
        if current is not None:
            current.append(line)
    if current is not None:
        records.append(current)
    return [parse_fields(r) for r in records]


def parse_fields(lines):
    """Parse one record's lines into {field: [values]}. Continuation lines are
    appended to the previous field, as ReDIF allows wrapped values."""
    fields = {}
    last = None
    for line in lines:
        match = re.match(r'^([A-Za-z][A-Za-z-]*):\s?(.*)$', line)
        if match:
            last = match.group(1)
            fields.setdefault(last, []).append(match.group(2).strip())
        elif last and line.strip():
            fields[last][-1] += ' ' + line.strip()
    return fields


def first(fields, key):
    values = fields.get(key)
    return values[0] if values else None


def existing_handles(directory, exclude, recursive=False):
    """Collect Handle: values from other .rdf files in `directory`.

    Non-recursive by default so this matches exactly the corpus that
    RePEcPopulator._load_existing_metadata() dedups against. Subdirectories
    such as archive/ hold superseded working copies of the same records, so
    counting them as "already deployed" would block every run.
    """
    handles = {}
    if not directory or not os.path.isdir(directory):
        return handles
    exclude = os.path.abspath(exclude)
    pattern = os.path.join(directory, '**', '*.rdf') if recursive else os.path.join(directory, '*.rdf')
    for path in sorted(glob.glob(pattern, recursive=recursive)):
        if os.path.abspath(path) == exclude:
            continue
        with open(path, encoding='utf-8', errors='replace') as handle_file:
            for line in handle_file:
                if line.startswith('Handle:'):
                    handles.setdefault(line.split(':', 1)[1].strip().lower(), path)
    return handles


def is_blacklisted(title, handle):
    haystack = f"{title or ''} {handle or ''}".lower()
    if any(token in haystack for token in BLACKLIST_SUBSTRINGS):
        return True
    if title and BLACKLIST_TITLE_RE.search(title):
        return True
    if handle and handle.rsplit(':', 1)[-1].lower() in BLACKLIST_SLUGS:
        return True
    return False


def validate(new_file, rdf_dir):
    with open(new_file, encoding='utf-8', errors='replace') as f:
        records = parse_records(f.read())

    blocking = []
    warnings = []

    # --- Blocking: duplicate handles within the new file ---
    seen = {}
    for index, record in enumerate(records, 1):
        handle = first(record, 'Handle')
        if not handle:
            continue
        key = handle.lower()
        if key in seen:
            blocking.append(
                f"Duplicate handle within new file: {handle} (records #{seen[key]} and #{index})"
            )
        else:
            seen[key] = index

    # --- Blocking: handles already deployed in other .rdf files ---
    prior = existing_handles(rdf_dir, new_file)
    for index, record in enumerate(records, 1):
        handle = first(record, 'Handle')
        if handle and handle.lower() in prior:
            blocking.append(
                f"Handle already exists in {os.path.basename(prior[handle.lower()])}: "
                f"{handle} (record #{index})"
            )

    # --- Warning only: overlap with superseded copies under subdirectories ---
    archived = existing_handles(rdf_dir, new_file, recursive=True)
    for index, record in enumerate(records, 1):
        handle = first(record, 'Handle')
        key = handle.lower() if handle else None
        if key and key in archived and key not in prior:
            warnings.append(
                f"Handle also appears in archived copy "
                f"{os.path.relpath(archived[key], rdf_dir)}: {handle} (record #{index})"
            )

    # --- Blocking: template / blacklisted entries ---
    for index, record in enumerate(records, 1):
        title, handle = first(record, 'Title'), first(record, 'Handle')
        if is_blacklisted(title, handle):
            blocking.append(f"Template/blacklisted entry (record #{index}): {handle} — {title!r}")

    # --- Blocking: missing required fields ---
    for index, record in enumerate(records, 1):
        missing = [f for f in REQUIRED_FIELDS if not first(record, f)]
        if missing:
            blocking.append(
                f"Record #{index} ({first(record, 'Handle') or 'no handle'}) "
                f"missing required field(s): {', '.join(missing)}"
            )

    # --- Warnings ---
    for index, record in enumerate(records, 1):
        label = f"record #{index} ({first(record, 'Handle') or 'no handle'})"

        handle = first(record, 'Handle')
        if handle and not HANDLE_RE.match(handle):
            warnings.append(f"Unexpected handle format in {label}: {handle}")

        number = first(record, 'Number')
        if not number or not NUMBER_RE.match(number):
            warnings.append(f"Unexpected number format in {label}: {number}")

        abstract = (first(record, 'Abstract') or '').strip()
        if abstract.lower().rstrip() in PLACEHOLDER_ABSTRACTS:
            warnings.append(f"Empty or placeholder abstract in {label}")

        doi = (first(record, 'DOI') or '').strip()
        if not doi or doi.lower() == 'none':
            warnings.append(f"Missing DOI in {label}")

    return records, blocking, warnings


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    new_file = sys.argv[1]
    rdf_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(new_file))

    if not os.path.isfile(new_file):
        print(f"❌ File not found: {new_file}")
        return 2

    records, blocking, warnings = validate(new_file, rdf_dir)

    print(f"\n{'=' * 62}")
    print(f"RePEc validation: {os.path.basename(new_file)}")
    print(f"{'=' * 62}")
    print(f"Total records:  {len(records)}")
    print(f"Blocking issues: {len(blocking)}")
    print(f"Warnings:        {len(warnings)}")

    if blocking:
        print("\n❌ BLOCKING ISSUES")
        for issue in blocking:
            print(f"   - {issue}")

    if warnings:
        print("\n⚠️  WARNINGS")
        for warning in warnings:
            print(f"   - {warning}")

    if blocking:
        print("\n❌ VALIDATION FAILED — do not deploy.\n")
        return 1

    print("\n✅ VALIDATION PASSED\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
