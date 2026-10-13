# Local credentials

Keep credentials in environment variables or ignored local configuration files.
The tracked `.env.example` contains placeholders only. Copy it to `.env` and fill
in the values locally; never commit that file.

The DOI utilities `check_dois.py`, `fix_doi_now.py`,
`fix_trailing_punctuation.py`, `restore_dois.py`, and `restore_dois_proper.py`
require non-empty `PUBPUB_EMAIL` and `PUBPUB_PASSWORD` environment variables.
They fail before making requests if either variable is missing or blank.
These scripts do not automatically load `.env`. In Bash or Zsh, load your own
local file before running a utility:

```sh
set -a
source .env
set +a
python scripts/utilities/check_dois.py
```

The API client accepts explicit `email` and `password` arguments, including
values read from an ignored local config. When an argument is omitted, it reads
the corresponding `PUBPUB_EMAIL` or `PUBPUB_PASSWORD` environment variable.
Explicit blank arguments are rejected rather than replaced with another login.
The exploratory notebook and its Python export require explicit keyword
arguments for both credentials; they have no default login.

The Coda setup wizard writes the supplied Coda key to the ignored `.env` file.
Its PubPub credential fields are blank for local completion. Coda scripts need
`CODA_API_KEY` plus the document/table settings used by the workflow.

Ignored paths include `.env`, `.env_do_not_share*`, `tests/conf_settings.py`,
and `conf.py`/`conf_contact.py` copies in any directory. Integration tests still
require their developer-only configuration and may create or delete live pubs.
Credential-configuration tests run offline:

```sh
python -m unittest discover -s tests -p test_credential_configuration.py -v
```

Removing credentials from current files does not revoke them or remove them
from Git history. Revoke exposed API tokens and rotate exposed account passwords
at their providers, then update the ignored local configs. History is unchanged.
