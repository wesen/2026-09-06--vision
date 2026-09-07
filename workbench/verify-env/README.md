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
