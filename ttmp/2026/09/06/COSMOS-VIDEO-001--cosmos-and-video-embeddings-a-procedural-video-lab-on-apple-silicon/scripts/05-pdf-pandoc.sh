#!/bin/sh
# BasicTeX fallback: plain code, readable type, separate contents page.
exec /opt/homebrew/bin/pandoc --no-highlight --toc --toc-depth=2 -V fontsize=11pt "$@"
