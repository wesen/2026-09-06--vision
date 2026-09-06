#!/bin/sh
# Reproduce the reviewed PDF locally. This script does not upload.
set -eu
cosmos_ticket_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cosmos_repo_dir=$(git -C "$cosmos_ticket_dir" rev-parse --show-toplevel)
PATH=/Library/TeX/texbin:$PATH
export PATH
remarquee upload md \
  "$cosmos_ticket_dir/design-doc/02-intern-guide-to-the-procedural-video-workbench.md" \
  --name 'COSMOS-VIDEO-001 Intern Guide' \
  --pdf-only --output-dir "$cosmos_repo_dir/output/pdf" \
  --pandoc "$cosmos_ticket_dir/scripts/05-pdf-pandoc.sh" \
  --pdf-engine /Library/TeX/texbin/xelatex \
  --mainfont Helvetica --monofont Menlo \
  --geometry 'margin=0.8in' \
  --latex-header-file "$cosmos_ticket_dir/scripts/04-pdf-header.tex" \
  --non-interactive
