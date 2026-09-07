"""Remove only an enclosing Markdown JSON fence; never repair payload contents.

Based on sanitize's markdown_fence_wrapper approach:
https://github.com/go-go-golems/sanitize/blob/c142cca399ff596da307d287fceda8de4155a3dd/pkg/json/fix.go
"""


def unwrap_json_fence(raw):
    """Return payload and a trace of wrapper removal, leaving other input intact."""
    lines = raw.strip().splitlines()
    if len(lines) >= 3 and lines[0].strip() in ('```json', '```') and lines[-1].strip() == '```':
        return '\n'.join(lines[1:-1]), ['markdown_fence_wrapper']
    return raw, []
