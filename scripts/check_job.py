#!/usr/bin/env python3
"""Validate opaque, public-only job declarations."""
import json
import os
from pathlib import Path
import re
import sys

KINDS = {
    "python-stdlib": Path("payload/main.py"),
    "python-science": Path("payload/main.py"),
    "lean-core": Path("profiles/lean-core/Proof.lean"),
    "lean-mathlib": Path("profiles/lean-mathlib/Proof.lean"),
}
ID = re.compile(r"[0-9a-f]{16,32}\Z")

def validate(root, branch):
    doc = json.loads((root / "job.json").read_text("utf-8"))
    if not isinstance(doc, dict) or set(doc) != {"version", "id", "kind"}:
        raise ValueError("Only version, id and kind are permitted")
    if type(doc["version"]) is not int or doc["version"] != 1:
        raise ValueError("Unsupported version")
    if not isinstance(doc["id"], str) or not ID.fullmatch(doc["id"]):
        raise ValueError("Identifier must be 16-32 lowercase hex characters")
    if branch != "jobs/" + doc["id"]:
        raise ValueError("Branch must match the manifest ID")
    if doc["kind"] not in KINDS:
        raise ValueError("Unsupported job kind")
    source = root / KINDS[doc["kind"]]
    if not source.is_file() or source.is_symlink() or not 0 < source.stat().st_size <= 131072:
        raise ValueError("Invalid or oversized source")
    for path in (root / "payload").rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink payloads are forbidden")
    if sum(p.stat().st_size for p in (root / "payload").rglob("*") if p.is_file()) > 2 * 1024 * 1024:
        raise ValueError("Payload exceeds 2 MiB")
    return doc

def main():
    root = Path(__file__).resolve().parents[1]
    branch = os.environ.get("GITHUB_REF_NAME") or (sys.argv[1] if len(sys.argv) > 1 else "")
    try:
        doc = validate(root, branch)
    except Exception as exc:
        print("VALIDATION_FAILED: " + str(exc), file=sys.stderr)
        return 2
    print("VALIDATION_OK", doc["id"], doc["kind"])
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
            out.write("kind=" + doc["kind"] + "\n")
            out.write("id=" + doc["id"] + "\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
