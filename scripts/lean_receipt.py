#!/usr/bin/env python3
"""Record result of a Lean compilation."""
import hashlib
import json
import os
from pathlib import Path
root = Path(__file__).resolve().parents[1]
kind = os.environ.get("PROOF_KIND", "lean-core")
if kind not in ("lean-core", "lean-mathlib"):
    raise SystemExit("Invalid proof kind")
src = root / "profiles" / kind / "Proof.lean"
manifest = json.loads((root / "job.json").read_text("utf-8"))
outcome = os.environ.get("BUILD_OUTCOME", "unknown")
receipt = {
    "version": 1, "id": manifest["id"], "kind": kind,
    "status": "passed" if outcome == "success" else "failed",
    "build_outcome": outcome,
    "commit": os.environ.get("GITHUB_SHA", "local-test"),
    "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
    "toolchain": (root / "profiles" / kind / "lean-toolchain").read_text("utf-8").strip(),
}
lock = root / "profiles" / kind / "lake-manifest.json"
if lock.is_file():
    receipt["lake_manifest_sha256"] = hashlib.sha256(lock.read_bytes()).hexdigest()
res = root / "result"
res.mkdir(exist_ok=True)
(res / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
print("RESULT_RECEIPT=" + json.dumps(receipt, sort_keys=True))
