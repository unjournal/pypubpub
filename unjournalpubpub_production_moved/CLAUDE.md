# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains Python scripts for managing academic evaluations on PubPub for The Unjournal. The main purpose is to create and manage evaluation packages for academic papers using the pypubpub library.

## Architecture

The codebase uses the `pypubpub` library (specifically v6 APIs) to interact with PubPub's platform. Scripts follow this pattern:

1. Import configuration from `conf.py` (email, password, community_id, community_url)
2. Create a config object using `record_pub_conf()`
3. Instantiate `EvaluationPackage` objects with paper DOIs or URLs
4. Evaluation packages can be created with empty evaluation placeholders (`{}`) when evaluators are not yet assigned

Key components:
- `EvaluationPackage`: Main class for creating evaluation packages on PubPub
- Papers can be referenced by DOI (e.g., "10.3386/w30011") or direct URL
- Community URL: https://unjournal.pubpub.org
- PubPub ID lookup tool: https://pubpub.tefkah.com/

## Environment Setup

Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:
```bash
pip install --verbose git+https://github.com/unjournal/pypubpub@main
pip install pytest bibtexparser nltk pycryptodome pyparsing pluggy python-slugify typing
```

Additional dependencies may be needed; check README if scripts fail.

## Configuration

The `conf.py` file contains authentication credentials and community settings. This file is gitignored and must be present locally with:
- `email`: PubPub login email
- `password`: PubPub login password (stored in G Collab, ask David)
- `community_url`: "https://unjournal.pubpub.org"
- `community_id`: "d28e8e57-7f59-486b-9395-b548158a27d6"

## Running Scripts

Execute scripts directly with Python:
```bash
python create_eval_01.py
python create_eval_clancy.py
python clean_out_evals.py
```

## Script Purposes

- `create_eval_01.py` / `create_eval_clancy.py`: Create evaluation packages for academic papers on PubPub
- `clean_out_evals.py`: Contains deletion functionality for pubs (via `delete_pub()` method)
- `scrapepubpub_attempt.py`: Web scraper for finding PubPub release URLs matching pattern `/pub/*/release/1`
