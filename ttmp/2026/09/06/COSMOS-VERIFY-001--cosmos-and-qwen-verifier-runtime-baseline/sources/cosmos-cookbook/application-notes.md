# Application notes: warehouse safety recipe

Archived upstream revision: `d0857364e8a727be41b181731e03f478213e4558`; see provenance.json for exact source URLs and hashes. The notebook, companion Python, setup, inference explanation, prompt guide, and license are stored beside this note. Downloaded code was read, not executed.

The recipe uses explicit visual class definitions and negative constraints to separate behavior from irrelevant environmental appearance. It processes video through Transformers, requests structured output, and stores predictions/errors for visual inspection in FiftyOne. The companion script samples at four fps and allows 1024 new tokens. Its parser removes Markdown fences. The prompt guide distinguishes direct structured responses from an explicitly requested reasoning format.

## Applied to this household system

- Define observable closed as a seated visible door, and observable open as visible displacement/opening. Absence of visible opening is insufficient for closed when the door cannot be inspected.
- Ask for target identification and door observability before the final predicate; make contradictory known/unobservable payloads invalid.
- Ignore actor activity as proof of door state. Keep an explicit unknown outcome, unlike a forced choice among safety classes.
- Preserve raw outputs, errors, source frames, annotated examples, and reviewed labels for later visual error analysis. Existing ticket image artifacts serve the immediate review need without adding FiftyOne.
- Retain the already implemented narrow fence unwrap; the recipe's global backtick replacement could change literal text inside JSON strings.

## Not adopted

We do not import warehouse class IDs, prioritize hazard labels, infer a post-intervention condition from one image, or switch this Mac to the notebook's CUDA setup. Our current point-state contract accepts one approved exact-time image. Four-fps video and 1024-token reasoning are distinct future capability/budget experiments, not settings silently changed in this comparison. The recipe is a useful design example, not evidence that our models become accurate under these changes.
