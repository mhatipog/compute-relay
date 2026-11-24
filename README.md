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
