# Real Link Issues Found on unjournal.pubpub.org

Generated: 2025-11-08

## Summary

Scanned 189 publications and found **real link issues** (excluding false positives):

1. **10 Broken Internal Links** - Links to other Unjournal pages that return 404
2. **DOIs with Extra Periods** - Causing 404 errors
3. **1 Malformed URL** - Incomplete URL ending in `/file`
4. **1 Charity Entrepreneur Dead Link**
5. **Draft Links with Access Tokens** - Potentially exposing private content

---

## 🔴 CRITICAL: Broken Internal Links (10 issues)

These are links from one Unjournal page to another that don't work:

### 1. Missing page: `evalsumceadiscounts`
Referenced from multiple pages but doesn't exist:
- https://unjournal.pubpub.org/pub/evalsumlimitedmeadprod
- https://unjournal.pubpub.org/pub/2dli3ws6
- https://unjournal.pubpub.org/pub/evalsumtemplateapplied

**Broken link:** `https://unjournal.pubpub.org/pub/evalsumceadiscounts#metrics`

**Fix:** Either create this page or update the links to point to the correct evaluation summary.

### 2. Draft link on published page
**Page:** https://unjournal.pubpub.org/pub/evalsumdemandfordemocracy
**Broken link:** https://unjournal.pubpub.org/pub/e1demandfordemocracy/draft

**Fix:** Remove `/draft` to link to the published version.

### 3. Missing template page
**Page:** https://unjournal.pubpub.org/pub/7s6czeed
**Broken link:** https://unjournal.pubpub.org/templates-applied-and-policy-stream

**Fix:** Create the templates page or remove the link.

### 4. Missing page: `om61yr2g`
**Page:** https://unjournal.pubpub.org/pub/evalsumanimalwelfarecost
**Broken link:** https://unjournal.pubpub.org/pub/om61yr2g#metrics

**Fix:** Link to the correct evaluation summary page.

### 5. Draft links with access tokens (potentially problematic)
**Pages:**
- https://unjournal.pubpub.org/pub/eval1psychotherapy
- https://unjournal.pubpub.org/pub/accelvaxeval2
- https://unjournal.pubpub.org/pub/accelvaxeval1

**Broken links:**
- `https://unjournal.pubpub.org/pub/evalsumpsychotherapy/draft?access=sl91tfox#metrics`
- `https://unjournal.pubpub.org/pub/dsvn99wo/draft?access=l21k3kty#metrics`

**Fix:** These should link to published versions, not drafts. Remove `/draft?access=...` part.

### 6. Missing dashboard link
**Page:** https://unjournal.pubpub.org/pub/se5q3jza
**Broken link:** https://unjournal.pubpub.org/dash/collection/completed-uj-evaluation-packages/overview

**Fix:** Update to correct dashboard URL or remove link.

---

## 🟡 DOIs with Extra Periods (5 issues)

DOIs that have periods at the end cause 404 errors. The period should be removed.

**Page:** https://unjournal.pubpub.org/pub/e2pharmpricing

**Broken DOIs:**
1. `https://doi.org/10.1001/jama.2024.25827.` ❌
   Should be: `https://doi.org/10.1001/jama.2024.25827` ✅

2. `https://doi.org/10.1086/707407.` ❌
   Should be: `https://doi.org/10.1086/707407` ✅

3. `https://doi.org/10.1017/bca.2022.12.` ❌
   Should be: `https://doi.org/10.1017/bca.2022.12` ✅

4. `https://doi.org/10.1162/rest_a_00849.` ❌
   Should be: `https://doi.org/10.1162/rest_a_00849` ✅

**Also:**

**Page:** https://unjournal.pubpub.org/pub/evalsumpopintuitions
- `https://doi.org/10.1017/CCOL0521825512\n` ❌ (has newline!)
  Should be: `https://doi.org/10.1017/CCOL0521825512` ✅

**Fix:** Edit these pages and remove the trailing periods from DOI links.

---

## 🟡 Malformed URL

**Page:** https://unjournal.pubpub.org/pub/e2strongminds
**Broken URL:** `https://www.unicef.org/mena/media/20381/file`

This URL is incomplete - it ends in `/file` without a filename.

**Fix:** Find the correct complete URL for this UNICEF resource.

---

## 🟡 Dead External Link

**Page:** https://unjournal.pubpub.org/pub/e2strongminds
**Broken link:** https://www.charityentrepreneurship.com/reports/edu-mass-comm

Returns 404 - the page has been removed or moved.

**Fix:** Check if there's a new URL for this Charity Entrepreneurship report, or remove the link.

---

## Recommended Actions

### Priority 1: Fix Internal Links (10 issues)
These are confusing for users and look unprofessional. Should be quick fixes:

1. Create missing `evalsumceadiscounts` page or redirect to correct page
2. Change `/draft` links to published versions
3. Create missing template pages or remove broken links
4. Remove access tokens from public links

**Estimated time:** 30 minutes

### Priority 2: Fix DOI Periods (5 issues)
Simple find-and-replace in one page:

**Page to edit:** https://unjournal.pubpub.org/pub/e2pharmpricing/draft
- Remove trailing periods from 4 DOI links
- Remove newline from 1 DOI link (on different page)

**Estimated time:** 5 minutes

### Priority 3: Fix Malformed/Dead Links (2 issues)
- Find correct UNICEF URL
- Find or remove Charity Entrepreneurship link

**Estimated time:** 10 minutes

---

## Quick Fix Script

I can create a script to automatically fix the DOI periods and some internal links. Would you like me to create that?

---

## Notes

- The backslash issues I initially reported are **false positives** - they render correctly on the site
- ChatGPT links are already being handled
- Many 403 errors (CGDev, HLI, UNICEF) are anti-bot protection, not dead links
