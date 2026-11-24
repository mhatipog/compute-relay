# Compute Relay
A neutral, public, reproducible calculation runner. No private scientific interpretations are stored here.

Four profiles: `python-stdlib`, `python-science` (pinned NumPy/SciPy), `lean-core` (Lean 4 without Mathlib), and `lean-mathlib` (with Mathlib caching).

## Submit
1. Create a branch `jobs/<16-to-32-lowercase-hex-characters>` from `main`.
2. Commit only the necessary public-safe source: `payload/main.py` for Python, or `profiles/lean-core/Proof.lean` or `profiles/lean-mathlib/Proof.lean` for Lean.
3. Commit `job.json` **last** containing exactly `{"version":1,"id":"<same-hex-id>","kind":"python-stdlib"}` (or another allowed kind). This triggers a GitHub-hosted workflow.
4. Inspect the Actions run; download the `result-<id>` artifact, and independently validate the receipt hashes. Python receipts are also printed to run logs.

## Privacy and execution rules
- **PUBLIC means public forever:** inputs, source, branch names, logs, artifacts, and history may be retained or indexed. Deleting branches is not an erasure guarantee.
- Never submit client data, credentials, unpublished science, private repository URLs, confidential parameters or personally identifiable information.
- This repository receives no private credentials and contains no context about why a job exists. A separate private system may map opaque IDs to private interpretations.
- All jobs run with `contents: read`, no stored secrets, fixed dependency profiles, a short timeout, no PR/issue-based execution, and one-day artifact retention.
- Executable inputs still run arbitrary code on an isolated public runner; submit only owner-reviewed sources. Resource caps bound time and output but do not provide full sandbox isolation.
- Results are computational evidence only, not independent scientific validation.


## Permitted use
This repository's GitHub-hosted CI is for developing, testing and publishing the **public Compute Relay software and its reproducibility fixtures**. It is not a general compute-for-hire service, background worker, or a way to offload unrelated private research. GitHub's additional Actions terms prohibit GitHub-hosted activity unrelated to the software project associated with the repository. Privately held workloads should run in the private project or on separately operated compute.

## Verified live profiles
- Python standard-library: 12! smoke fixture, successful with hashed data artifact.
- Python-science: pinned NumPy/SciPy, integration fixture, successful with hashed data artifact.
- Lean Core: Lean 4.24 standalone proof fixture, successful kernel build.
- Lean Mathlib: Lean 4.24 + Mathlib v4.24 fixture, successful kernel build and cache support.

The first public lean-core build failed because the dependency manifest was missing. The pinned manifests were subsequently committed and both Lean profiles passed. The source histories and failure logs remain public. GitHub artifact retention is one day; use the verified receipts and your private record to preserve results.
