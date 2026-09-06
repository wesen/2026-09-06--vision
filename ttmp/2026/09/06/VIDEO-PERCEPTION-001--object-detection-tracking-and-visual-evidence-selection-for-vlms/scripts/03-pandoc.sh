#!/bin/sh
perception_script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec /opt/homebrew/bin/pandoc --resource-path="$perception_script_dir/../design-doc" --no-highlight --toc --toc-depth=2 -V fontsize=11pt "$@"
