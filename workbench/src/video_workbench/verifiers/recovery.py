"""Traced recovery of one observed missing-close wrapper; never alter JSON."""
from .visibility import parse_experiment, parse_visibility

RECOVERY_VERSION = 'missing-reasoning-close-v1'


def parse_with_recovery(request, raw, profile, finish_reason=None):
    """Strict first; accept one line-start final JSON after an unclosed opener.

    Earlier braces/fences or mixed reasoning tags make the boundary ambiguous.
    The original raw response is preserved; content/citation checks stay strict.
    """
    strict = parse_experiment(request, raw, profile, finish_reason)
    if strict['status'] == 'ok' or profile['prompt_style'] != 'reasoning':
        return strict
    if strict.get('reason') != 'incomplete or repeated reasoning envelope':
        return strict
    opening, closing = ('<reasoning>', '</reasoning>') if profile['model_family']=='qwen' else ('<think>', '</think>')
    value = raw.strip()
    if not value.startswith(opening) or value.count(opening) != 1 or closing in value:
        return strict
    body = value[len(opening):]
    if any(tag in body for tag in ('<think>', '</think>', '<reasoning>', '</reasoning>')):
        return strict
    offset = 0
    for line in body.splitlines(keepends=True):
        if line.lstrip().startswith('{') or line.strip() in ('```', '```json'):
            prefix, final = body[:offset], body[offset:]
            # Do not choose among competing JSON objects or fenced blocks.
            if not prefix.strip() or any(marker in prefix for marker in ('{', '}', '```')):
                return strict
            checked = parse_visibility(request, final)
            if checked['status'] != 'ok':
                return strict
            return dict(checked, raw=raw, final_text=final, schema_version=strict['schema_version'],
                output_style=profile['prompt_style'],
                normalizations=['missing_reasoning_close_before_final_json', *checked['normalizations']],
                recovery=dict(version=RECOVERY_VERSION, missing_token=closing,
                    final_start_character=len(raw)-len(raw.lstrip())+len(opening)+offset,
                    strict_reason=strict['reason']))
        offset += len(line)
    return strict
