# Local verifier runtime

This isolated environment uses the existing workbench lockfile with the
`pooled-images` extra (MLX-VLM 0.6.17). It serves generative image verifier
candidates; the name of the reused dependency extra does not make their
outputs embeddings. Existing pooled and repaired native-video environments
remain separate.

```sh
UV_PROJECT_ENVIRONMENT="$PWD/workbench/verify-env/.venv" \
  uv sync --project workbench --extra pooled-images --frozen
```

Candidate revisions and download instructions are recorded in
`ttmp/2026/09/06/COSMOS-VERIFY-001--cosmos-and-qwen-verifier-runtime-baseline/`.
The image gate launches one candidate at a time and kills its process group
on a 120-second timeout. It checks local image hashes before generation.
A successful generation or valid JSON is not factual acceptance.

The 8B follow-up uses ticket script `05-download-8b.py` to pin Qwen's
public 8-bit MLX conversion and official Cosmos weights. Script
`06-convert-cosmos-8b.py` converts Cosmos locally with MLX-VLM 0.6.17,
8-bit affine quantization, and group size 64, recording output hashes.
This conversion has not been accepted as numerically equivalent to the
full-precision model. Its unquantized source is retained separately.
The image gate accepts `--pins FILE --output DIRECTORY` to preserve the
original 2B results. The archive script similarly accepts `--source` and
`--destination`; figures can be regenerated without running models.
