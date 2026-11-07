#!/usr/bin/env bash
# Optional updater for a self-hosted Ubuntu installation of this repository.
# Install as a systemd timer only after configuring the environment variables.
set -euo pipefail
: "${SPOILER_REPO_DIR:?SPOILER_REPO_DIR is required}"
: "${SPOILER_SERVICE:?SPOILER_SERVICE is required}"
: "${SPOILER_VENV_PYTHON:?SPOILER_VENV_PYTHON is required}"
if [[ ! -d "$SPOILER_REPO_DIR/.git" ]]; then
  echo "Repository is not a git checkout: $SPOILER_REPO_DIR" >&2; exit 1
fi
if [[ -n "$(git -C "$SPOILER_REPO_DIR" status --porcelain)" ]]; then
  echo "Local changes detected. Refusing to overwrite them." >&2; exit 1
fi
before=$(git -C "$SPOILER_REPO_DIR" rev-parse HEAD)
git -C "$SPOILER_REPO_DIR" fetch origin main --quiet
after=$(git -C "$SPOILER_REPO_DIR" rev-parse origin/main)
if [[ "$before" == "$after" ]]; then exit 0; fi
# Validate the incoming source before changing the running checkout.
git -C "$SPOILER_REPO_DIR" show "origin/main:main.py" | "$SPOILER_VENV_PYTHON" -c 'import ast,sys;ast.parse(sys.stdin.read())'
git -C "$SPOILER_REPO_DIR" show "origin/main:media_test.py" | "$SPOILER_VENV_PYTHON" -c 'import ast,sys;ast.parse(sys.stdin.read())'
git -C "$SPOILER_REPO_DIR" merge --ff-only origin/main
"$SPOILER_VENV_PYTHON" -m pip install -r "$SPOILER_REPO_DIR/requirements.txt"
"$SPOILER_VENV_PYTHON" -m py_compile "$SPOILER_REPO_DIR/main.py" "$SPOILER_REPO_DIR/media_test.py"
systemctl restart "$SPOILER_SERVICE"
echo "Updated spoiler bot to $after"
