# Video Understanding for Procedural Work — laboratory companion

These files accompany Chapters 20 and 21 of the textbook. They contain executable teaching examples with synthetic inputs, not a trained video model or a production worker-monitoring service.

## Sequence laboratory

Create a Python environment, install NumPy, and run from this directory:

```sh
python -m pip install -r requirements-sequence.txt
python sequence_lab.py
python -m unittest -v test_labs.py
```

The sequence laboratory includes log-space forward and backward inference, Viterbi decoding, a bounded-duration HSMM, segment helpers, and simplified prerequisite and persistence monitors. The 20 regression tests include exhaustive comparisons on tiny HMM and HSMM instances, impossible paths, missing evidence, and timestamp checks.

Run demonstrations without Python's `-O` option: that option disables their assertions. The separate regression suite uses `unittest` assertions.

## Neural laboratory

The neural laboratory additionally requires PyTorch. Install the appropriate CPU or accelerator build for your environment using the official PyTorch installation guidance, then run:

```sh
python neural_lab.py
```

The tested environment used Python 3.13.5, NumPy 2.3.5, and PyTorch 2.10.0+cpu. No camera, VSS installation, or GPU is needed for these small tests. The neural example is a causal multi-stage teaching variant, not a paper-exact reproduction of MS-TCN.

It checks output dimensions, invariance of prefix predictions to future perturbations, full-versus-prefix equivalence, an all-invalid masked loss, and a synthetic optimizer smoke test. The feature vectors in the optimizer test directly encode the target classes, so the loss reduction is not a video-recognition benchmark.

## Recorded outputs

`sequence_output.json` and `neural_output.json` contain the outputs produced for this edition. `test_output.txt` records the successful regression run. Floating-point values and elapsed test time may vary with the environment; the invariants and stated tolerances are the meaningful checks.

## Deliberate limitations

The HSMM is offline, has bounded durations, requires finite observation potentials, and treats the final segment as completed. It does not implement an online censored-duration filter.

The prerequisite monitor is monotone and has a single conservative coverage flag. It does not implement rework invalidation or interval-specific evidence reconciliation. The persistence gate's internal reset on missing evidence does not resolve a durable production incident; the caller must handle the observation-gap event separately.

The neural module expects already prepared features. Its causal tests do not prove that an upstream video encoder is causal. Padding masks are not a complete camera-outage policy. No VSS, Kafka, VIOS, or Triton integration is implemented or claimed.

The textbook explains these limitations, supplies the mathematical derivations, and defines the additional state, evaluation, and recovery contracts required for a deployment.
