# Configuring PubPub API (V6) for The Unjournal

1. To be useable and clearly understand what functions do

- to enable ad-hoc adjustments and bulk fixes
- to build other functionality and integrations

2. To try to automate The Unjournal's production process

- Mainly building the 'evaluation packages'

- Also to build metadata files for RePEc
- Enable other feeds and updates (e.g., evaluation data reporting)

## Project management

Coda task: [Work w/ PubPub API](https://coda.io/d/_dOyXJoZ6imx#All-unfinished-current-Tasks_tuXFw/r159&view=modal)

See subtasks within

## Folders and content

pypubpub: the actual code adapting the api to do operations

tests: trying it out

Moved to https://github.com/daaronr/unjournalpubpub_production -- production_work: actual work for real on the pubpub V6 content. Keeping track of what was done

repec_rdfs: rdf files created to add to repec (but how did we create them again?)
--> instructions in  https://github.com/daaronr/unjournalpubpub_production

notebooks: Work from Google collab

## Utility Scripts

### delete_untitled_pubs.py

Utility script to find and delete all publications with titles starting with "untitled pub".

**Usage:**
```bash
PASSWORD="your-password" .venv/bin/python delete_untitled_pubs.py
```

**Features:**
- Searches for all pubs with titles matching "untitled pub" (case-insensitive)
- Displays a list of all matching pubs before deletion
- Provides progress feedback during batch deletion
- Generates a summary report of successful and failed deletions

**Security Note:** Requires `PASSWORD` environment variable to be set. The script uses credentials from `tests/conf_settings.py`, which is gitignored and should never be committed with real passwords.

### Scratch work on fixes

https://testabcd123456789.pubpub.org/pub/nudgesincreasewelfare6648/draft

- Need quotes around paper title (fancy -- replace quotation marks in title with single quotes)

- Need to be able to specify multiple authors
    - for evaluation summary this is evaluator 1, evaluator 2, ..., eval. manager 1 (eval. manager 2)

- Evaluations
    - title should include the evaluation number... 'evaluation 1 of [papertitle]'
    - connection ... it should also be listed as 'review of the ' [original research]



## Scratch work and notes

https://colab.research.google.com/drive/15gSHFLqHubhtCJH-uW5z5R9g6I-57-th#scrollTo=xBnL02vEg6l0

https://colab.research.google.com/drive/1kj9njUpJkJ6hAxrLaUi4EYeZu0u9L1O_#scrollTo=tVSbFxNISAEG

https://docs.google.com/document/d/1F9w46tN3u8eeE8f5iTi543eDxAf9BTJ1OXJgxDHtPsw/edit#heading=h.57ljlv1pdkue
