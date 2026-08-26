#!/usr/bin/env bash
#
# End-to-end RePEc metadata refresh: pull, generate, clean, validate, deploy, commit.
#
# Paths are resolved relative to this script, so it runs from any checkout on any
# machine -- no hardcoded home directory.
#
# Usage:
#   scripts/repec_refresh.sh                 # full run
#   scripts/repec_refresh.sh --dry-run       # generate + validate only, no deploy/commit
#   scripts/repec_refresh.sh --no-deploy     # skip the Linode upload
#   scripts/repec_refresh.sh --no-push       # commit locally but do not push
#   scripts/repec_refresh.sh --no-pull       # skip the git pull
#
# Exit codes: 0 success (including "nothing new"), 1 failure/blocked.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RDF_DIR="$REPO_ROOT/repec_rdfs"
SERVER="${REPEC_SERVER:-root@45.56.106.79}"
REMOTE_DIR="${REPEC_REMOTE_DIR:-/var/lib/repec/rdf}"

DO_PULL=1; DO_DEPLOY=1; DO_COMMIT=1; DO_PUSH=1
for arg in "$@"; do
  case "$arg" in
    --dry-run)   DO_DEPLOY=0; DO_COMMIT=0; DO_PUSH=0 ;;
    --no-deploy) DO_DEPLOY=0 ;;
    --no-commit) DO_COMMIT=0; DO_PUSH=0 ;;
    --no-push)   DO_PUSH=0 ;;
    --no-pull)   DO_PULL=0 ;;
    -h|--help)   sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

step() { printf '\n=== %s ===\n' "$1"; }
fail() { printf '\n❌ %s\n' "$1" >&2; exit 1; }

# --- Pick a Python interpreter -----------------------------------------------
PYTHON=""
for candidate in \
    "${REPEC_PYTHON:-}" \
    "$REPO_ROOT/.venv312/bin/python" \
    "$REPO_ROOT/.venv/bin/python" \
    /opt/homebrew/Caskroom/miniforge/base/bin/python3 \
    "$(command -v python3 2>/dev/null)"; do
  if [ -n "$candidate" ] && [ -x "$candidate" ]; then PYTHON="$candidate"; break; fi
done
[ -n "$PYTHON" ] || fail "No usable Python interpreter found."
echo "Repo:   $REPO_ROOT"
echo "Python: $PYTHON"

# --- Preflight: credentials must be present ----------------------------------
if [ ! -f "$REPO_ROOT/tests/conf_settings.py" ] \
   && [ -z "${PUBPUB_COMMUNITY_ID:-}" ]; then
  fail "No PubPub credentials. Create tests/conf_settings.py or set PUBPUB_COMMUNITY_ID / PUBPUB_EMAIL / PUBPUB_PASSWORD.
This script must run where those credentials exist (it will not work in an ephemeral cloud container)."
fi

# --- Step 1: pull -------------------------------------------------------------
if [ "$DO_PULL" -eq 1 ]; then
  step "Pulling latest code"
  git -C "$REPO_ROOT" pull origin main || fail "git pull failed -- resolve manually before rerunning."
fi

# --- Step 2: generate ---------------------------------------------------------
step "Generating RDF"
mkdir -p "$RDF_DIR"
BEFORE="$(mktemp)"; ls "$RDF_DIR"/evalX_*.rdf 2>/dev/null | sort > "$BEFORE"

"$PYTHON" "$REPO_ROOT/scripts/generate_and_deploy_repec.py" \
    --skip-deploy --output-dir "$RDF_DIR" || fail "Generation failed."

AFTER="$(mktemp)"; ls "$RDF_DIR"/evalX_*.rdf 2>/dev/null | sort > "$AFTER"
GENERATED="$(comm -13 "$BEFORE" "$AFTER" | tail -1)"
rm -f "$BEFORE" "$AFTER"

# Fall back to the newest evalX file if the name was reused within the same second.
if [ -z "$GENERATED" ]; then
  GENERATED="$(ls -t "$RDF_DIR"/evalX_*.rdf 2>/dev/null | head -1)"
fi
[ -n "$GENERATED" ] && [ -f "$GENERATED" ] || fail "No RDF file was generated."
echo "Generated: $GENERATED"

# --- Step 3: clean ------------------------------------------------------------
step "Cleaning (unicode + placeholder abstracts)"
"$PYTHON" "$REPO_ROOT/scripts/clean_repec_rdf.py" "$GENERATED" "$GENERATED" \
  || fail "Cleaning failed."

# --- Step 5 (early): record count --------------------------------------------
COUNT="$(grep -c '^Handle:' "$GENERATED" || true)"
echo "Records in new file: $COUNT"

if [ "$COUNT" -eq 0 ]; then
  step "Nothing new"
  echo "✅ 0 new records -- every published pub is already covered."
  echo "Skipping validation, deploy and commit. Removing empty file."
  rm -f "$GENERATED"
  exit 0
fi
if [ "$COUNT" -gt 50 ]; then
  echo "⚠️  $COUNT records is unusually high for a routine refresh -- review the diff."
fi

# --- Step 4: validate (blocking) ---------------------------------------------
step "Validating"
if ! "$PYTHON" "$REPO_ROOT/scripts/validate_repec_rdf.py" "$GENERATED" "$RDF_DIR"; then
  # Quarantine the bad file. The generator treats every *.rdf directly inside
  # repec_rdfs/ as already-published and skips those handles, so leaving a
  # rejected file in place would silently drop those evaluations from every
  # future run. It globs non-recursively, so a subdirectory is safe.
  mkdir -p "$RDF_DIR/failed"
  QUARANTINED="$RDF_DIR/failed/$(basename "$GENERATED")"
  mv "$GENERATED" "$QUARANTINED"
  fail "Validation found blocking issues. Not deploying.
The rejected file was moved out of the active directory so it cannot suppress
these records on the next run:
  $QUARANTINED"
fi

# --- Step 6: deploy -----------------------------------------------------------
DEPLOY_STATUS="skipped"
if [ "$DO_DEPLOY" -eq 1 ]; then
  step "Deploying to $SERVER"
  REMOTE_NAME="unjournal_eval_$(date +%Y%m%d).rdf"
  if scp "$GENERATED" "$SERVER:$REMOTE_DIR/$REMOTE_NAME" \
     && ssh "$SERVER" "cd $REMOTE_DIR && ln -sf $REMOTE_NAME latest.rdf"; then
    echo "Uploaded as $REMOTE_NAME; latest.rdf now points at it."
    ssh "$SERVER" "wc -l $REMOTE_DIR/$REMOTE_NAME" || true
    DEPLOY_STATUS="succeeded"
  else
    echo "⚠️  Deploy failed. The validated file is still good and will be committed." >&2
    DEPLOY_STATUS="failed"
  fi
fi

# --- Step 7: commit and push --------------------------------------------------
GIT_STATUS="skipped"
if [ "$DO_COMMIT" -eq 1 ]; then
  step "Committing"
  git -C "$REPO_ROOT" add "$RDF_DIR"
  if git -C "$REPO_ROOT" diff --cached --quiet; then
    echo "Nothing staged to commit."
  else
    git -C "$REPO_ROOT" commit \
      -m "Automated RePEc metadata refresh: $COUNT new records ($(date +%Y-%m-%d))" \
      && GIT_STATUS="committed"
    if [ "$DO_PUSH" -eq 1 ] && [ "$GIT_STATUS" = "committed" ]; then
      if git -C "$REPO_ROOT" push origin main; then
        GIT_STATUS="committed and pushed"
      else
        echo "⚠️  Push failed -- commit is local. Do not force-push; resolve manually." >&2
        GIT_STATUS="committed, push failed"
      fi
    fi
  fi
fi

# --- Summary ------------------------------------------------------------------
step "Summary"
printf 'New records:  %s\n' "$COUNT"
printf 'Validation:   passed\n'
printf 'Deployment:   %s\n' "$DEPLOY_STATUS"
printf 'Git:          %s\n' "$GIT_STATUS"
printf 'File:         %s\n' "$GENERATED"
