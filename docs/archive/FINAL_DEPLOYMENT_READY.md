# Final RDF File - Ready for Deployment (CORRECTED)

## ✅ Issue Fixed: Correct Abstracts Now Used

**Problem Identified:** The "enriched" file incorrectly used the **original paper's abstracts** instead of the **evaluation's abstracts**.

**Solution:** Use the template abstracts, which correctly identify each record as an evaluation.

## File to Deploy

**USE THIS FILE:**
```
repec_rdfs/eval2025_04.rdf
```

- **Records**: 22 evaluations (2025-47 to 2025-68)
- **Abstracts**: Correct template format
- **Size**: 278 lines, 13 KB

**DO NOT USE:**
- ❌ `eval2025_04_enriched.rdf` - Has wrong abstracts (paper abstracts)
- ❌ `eval2025_04_test.rdf` - Test file only

## Correct Abstract Format

### ✅ Individual Evaluations
```
Title: Evaluation 1 of "Maternal cash transfers for gender equity..."
Abstract: Evaluation of "Maternal cash transfers for gender equity..." for The Unjournal.
```

### ✅ Evaluation Summaries
```
Title: Evaluation Summary and Metrics: "Maternal cash transfers..."
Abstract: Evaluation Summary and Metrics: "Maternal cash transfers..." for The Unjournal.
```

### ✅ Author Responses
```
Title: Authors' response to Unjournal evaluations of "Paper Title"
Abstract: [blank or brief description]
```

## Why These Abstracts Are Correct

1. **Clear identification**: Immediately tells reader this is an evaluation, not the original paper
2. **Prevents confusion**: Won't be mistaken for the original research
3. **Proper attribution**: Makes it clear these are Unjournal products
4. **Google Scholar compatible**: Standard format for reviews/evaluations

## Citation Linking to Original Papers

### How Google Scholar Will Link Your Evaluations as Citations

For your evaluations to appear in the "Cited by" list of the original papers, Google Scholar needs to find **references** to those papers in your evaluation content.

**Critical Requirement:** Each PubPub evaluation page MUST have a "References" section citing the original paper.

### Check Your PubPub Pages

Visit a sample evaluation:
```
https://unjournal.pubpub.org/pub/e2maternalcashtransfers
```

**Look for:**
- [ ] A "References" or "Bibliography" heading
- [ ] A formal citation to the original paper being evaluated
- [ ] The citation includes: Authors, Title, Year, DOI

### If References Are Missing → Add Them

**Add to each evaluation on PubPub:**

```markdown
## References

Smith, J., Jones, M., & Brown, K. (2023). Maternal cash transfers for
gender equity and child development: Experimental evidence from India.
*Working Paper*. https://doi.org/10.1234/example
```

**Google Scholar will:**
1. Crawl your PubPub evaluation page
2. Find the References section
3. Parse the citation to the original paper
4. Add your evaluation to the "Cited by" list of that paper

### Timeline
- Add References to PubPub: **Week 0**
- Deploy RDF to RePEc: **Week 1**
- Google Scholar indexes evaluations: **Weeks 2-4**
- Citation links appear: **Weeks 8-12**

## Papers Being Evaluated (9 unique papers)

Your 22 evaluation records cover these 9 papers:

1. Asymmetry in Civic Information (Togo tax participation)
2. Meaningfully reducing meat consumption (meta-analysis)
3. Social safety nets and women's agency
4. Ends versus Means (Kantians, Utilitarians)
5. Forecasts of cultured meat production
6. Maternal cash transfers (India)
7. Irrigation and climate resilience (Mali)
8. Online fundraising and charitable giving (Facebook)
9. Scale-Use Heterogeneity in well-being

Each needs proper References sections on PubPub for citation linking.

## Deployment Steps

### 1. **FIRST: Update PubPub** (if not already done)

For each of the 22 evaluations, ensure there's a References section:

```bash
# Check a few samples:
https://unjournal.pubpub.org/pub/e2civicasymmetry
https://unjournal.pubpub.org/pub/e1maternalcashtransfers
https://unjournal.pubpub.org/pub/evalsumheterogenity
```

If missing References sections, add them before deploying to RePEc.

### 2. **THEN: Deploy RDF to Linode**

```bash
# Upload the correct file
scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/

# Verify upload
ssh root@45.56.106.79 "ls -lah /var/lib/repec/rdf/eval2025_04.rdf"
```

### 3. **Monitor Indexing**

| Timeline | Check |
|----------|-------|
| Week 1 | RePEc IDEAS: https://ideas.repec.org/s/bjn/evalua.html |
| Week 2-4 | Google Scholar: Search for evaluation titles |
| Week 8-12 | Check original papers' "Cited by" lists |

## Example: Perfect Setup for Citation Linking

**Original Paper** (published elsewhere):
```
Title: Maternal cash transfers for gender equity...
DOI: 10.1234/example
Location: NBER Working Papers, arXiv, etc.
Google Scholar: ✓ Indexed
```

**Your Evaluation** (on PubPub):
```markdown
# Evaluation 2 of "Maternal cash transfers..."

[Evaluation content]

## References

Smith, J., Jones, M., & Brown, K. (2023). Maternal cash transfers for
gender equity and child development: Experimental evidence from India.
NBER Working Paper No. 12345. https://doi.org/10.1234/example
```

**Result:**
- Google Scholar indexes your evaluation
- Parses the References section
- Links your evaluation in the "Cited by" list of the original paper ✓

## Anonymous Evaluators (Non-Issue)

```
Author-Name: Evaluator 1
```

This is **fine** for citation linking. Google Scholar cares about:
- ✓ The evaluation exists and is indexed
- ✓ The References section cites the original paper
- ✗ Who wrote it (doesn't matter)

So anonymous evaluations will still create citation links to the original papers.

## Final Checklist

- [x] Correct RDF file prepared (eval2025_04.rdf with template abstracts)
- [ ] PubPub evaluations have References sections (check and add if needed)
- [ ] Linode server access verified
- [ ] RDF file deployed to `/var/lib/repec/rdf/eval2025_04.rdf`
- [ ] Wait for RePEc indexing (1-2 weeks)
- [ ] Wait for Google Scholar indexing (2-4 weeks)
- [ ] Verify citation links (8-12 weeks)

## Files Summary

```
✅ USE: repec_rdfs/eval2025_04.rdf
   - 22 records, correct abstracts
   - Template format: "Evaluation of [Paper Title] for The Unjournal"

❌ DON'T USE: repec_rdfs/eval2025_04_enriched.rdf
   - Has original paper abstracts (wrong!)

📄 Reference: repec_rdfs/evalX_13_50_40.rdf
   - Full export (193 records, all time)
```

## Next Action

**Deploy when ready:**
```bash
scp repec_rdfs/eval2025_04.rdf root@45.56.106.79:/var/lib/repec/rdf/
```

The file is correct and ready!
