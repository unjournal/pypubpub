# Link Issues Report for unjournal.pubpub.org

Generated: 2025-11-07

## Executive Summary

Scanned **189 published publications** on unjournal.pubpub.org and found:

- 🤖 **11 ChatGPT thread links** - **10 are NOT accessible** (91% failure rate)
- ❌ **246 broken URLs with trailing backslashes** - affecting **103 publications** (54%)
- ⚠️ **6 false positives** (utm_source=chatgpt.com tags, not actual ChatGPT links)

## Critical Issues

### 1. ChatGPT Links - MOSTLY INACCESSIBLE

**10 out of 11 ChatGPT links cannot be viewed** (404 or 403 errors).

#### Inaccessible ChatGPT Links (10):

**Publication: "Irrigation Strengthens Climate Resilience"**
- https://unjournal.pubpub.org/pub/evalsumirrigationresilience
- 6 broken ChatGPT links:
  - https://chatgpt.com/share/68cac67f-c910-8002-8d46-3136923f78f6 (404)
  - https://chatgpt.com/share/68caa95a-6a10-8002-b2a7-63207a114685 (404)
  - https://chatgpt.com/share/68cc1a93-b28c-8002-b3dc-776ec7f8e42d (404)
  - https://chatgpt.com/s/t_68cbe6b375988191974ad9694e112cab (403)
  - https://chatgpt.com/share/68cac869-fdf0-8002-8323-825a9b7c5e30 (404)
  - https://chatgpt.com/share/68cc1a33-0c24-8002-bd7b-c9e49cfa8805 (404)

**Publication: "Adaptability and the Pivot Penalty in Science and Technology"**
- https://unjournal.pubpub.org/pub/evalsumpivotpenalty
- https://unjournal.pubpub.org/pub/e1pivotpenalty
- 4 broken ChatGPT links:
  - https://chatgpt.com/share/67db35be-85d0-8002-abad-aa7862117a25 (404)
  - https://chatgpt.com/share/67db33c5-a260-8002-81e8-633904aef9df (404)
  - https://chatgpt.com/share/67db09ee-f4fc-8002-8cf5-606e6c761c89\ (403) **[Also has trailing backslash]**

#### Accessible ChatGPT Link (1):

**Publication: "Intergenerational Child Mortality Impacts of Deworming"**
- https://unjournal.pubpub.org/pub/evalsumintergendeworming
- ✅ https://chatgpt.com/share/e588be50-d63d-4320-9a5a-3bcbf077f63a (200 OK)

### 2. Trailing Backslash Issues - SYSTEMATIC BUG

**246 URLs with trailing backslashes** `\` are broken across **103 publications** (54% of all pubs).

This is a systematic formatting bug. When URLs end with `\`, they return 404 errors.

#### Top 10 Most Affected Publications:

1. **"Does online fundraising increase charitable giving?"** (e2fundraisingcharitablegivingreiley)
   - 10 broken links
   - Edit: https://unjournal.pubpub.org/pub/e2fundraisingcharitablegivingreiley/draft

2. **"The wellbeing cost effectiveness of StrongMinds"** (evalsumstrongminds)
   - 2 broken links
   - Edit: https://unjournal.pubpub.org/pub/evalsumstrongminds/draft

3. **"Accelerating Vaccine Innovation"** (accelvax)
   - 1 broken link
   - Edit: https://unjournal.pubpub.org/pub/accelvax/draft

... and 100 more publications with this issue.

## Recommended Fixes

### Fix 1: Remove/Replace Inaccessible ChatGPT Links

**Why they're broken:** ChatGPT shared conversations can be:
1. Deleted by the creator
2. Made private
3. Expired (OpenAI may have changed their sharing policies)

**Recommended actions:**

1. **For the Irrigation Resilience evaluation:**
   - Contact the evaluator/author
   - Ask them to re-share the conversations or provide:
     - Screenshots of the key ChatGPT interactions
     - Summary text of what was discussed
     - Archive links if available
   - Edit: https://unjournal.pubpub.org/pub/evalsumirrigationresilience/draft

2. **For the Pivot Penalty evaluation:**
   - Same process as above
   - Edit: https://unjournal.pubpub.org/pub/evalsumpivotpenalty/draft
   - Edit: https://unjournal.pubpub.org/pub/e1pivotpenalty/draft

3. **Keep the accessible link:**
   - https://unjournal.pubpub.org/pub/evalsumintergendeworming
   - This one works! ✅

### Fix 2: Remove Trailing Backslashes (CRITICAL)

This is the most important fix as it affects 54% of publications.

**Automated fix approach:**

I can create a script to automatically fix all trailing backslashes using the PubPub API:

1. For each affected pub:
   - Fetch the current text content
   - Find and replace all URLs ending with `\`
   - Remove the trailing backslash
   - Update the pub via API

**Manual fix approach:**

For each affected pub:
1. Open in edit mode (`/draft`)
2. Use Find & Replace (Ctrl+F / Cmd+F)
3. Find: URLs ending with `\`
4. Replace: Remove the trailing `\`

**Example fixes:**

```
❌ https://doi.org/10.2139/ssrn.2683621\
✅ https://doi.org/10.2139/ssrn.2683621

❌ https://doi.org/10.1287/mksc.2022.0357\
✅ https://doi.org/10.1287/mksc.2022.0357
```

### Complete list of affected pubs

See `quick_scan_results.json` for the complete list of 103 publications with trailing backslash issues.

## Scripts Available

I've created several scripts to help with this:

1. **scan_links.py** - Full scan with link testing (takes longer)
2. **quick_scan_chatgpt.py** - Fast scan for ChatGPT links and formatting issues
3. **test_chatgpt_links.py** - Tests ChatGPT links for accessibility
4. **fix_trailing_backslashes.py** - Generates fix instructions

## Next Steps

### Immediate Actions:

1. **Fix trailing backslashes** in the 103 affected publications (highest priority)
2. **Contact authors** of publications with broken ChatGPT links
3. **Remove or replace** the 10 inaccessible ChatGPT links

### Prevention:

1. **Review the content import/export process** - The trailing backslash issue suggests a systematic problem in how content is being processed
2. **Consider a policy** on external links:
   - Archive important conversations (via archive.org or screenshots)
   - Discourage linking to ephemeral content like ChatGPT threads
   - Use permanent hosting for supporting materials

## Detailed Results Files

- `quick_scan_results.json` - All issues found
- `chatgpt_accessibility_results.json` - Detailed ChatGPT link testing results
- `link_scan_results.json` - Full link scan results (if complete)

## Questions?

Run the scripts again at any time:
```bash
python quick_scan_chatgpt.py        # Fast scan
python test_chatgpt_links.py        # Test ChatGPT accessibility
python fix_trailing_backslashes.py  # Generate fix instructions
```
