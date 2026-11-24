#!/usr/bin/env python3
"""Bounded public calculation and hashed result receipt."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "result"
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    RESULT.mkdir(exist_ok=True)
    src = ROOT / "payload/main.py"
    started = time.monotonic()
    status, code = "failed", -1
    with (RESULT / "stdout.txt").open("wb") as out, (RESULT / "stderr.txt").open("wb") as err:
        try:
            run = subprocess.run(
                [sys.executable, "-I", str(src)], cwd=ROOT, stdout=out, stderr=err,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                timeout=180, check=False,
            )
            code = run.returncode
            status = "passed" if code == 0 else "failed"
        except subprocess.TimeoutExpired:
            code, status = 124, "timeout"
    if (RESULT / "stdout.txt").stat().st_size + (RESULT / "stderr.txt").stat().st_size > 1024 * 1024:
        code, status = 125, "output_limit"
        for name in ("stdout.txt", "stderr.txt"):
            with (RESULT / name).open("r+b") as handle:
                handle.truncate(524288)
    files = {}
    total = 0
    for path in sorted(RESULT.rglob("*")):
        if path.is_symlink():
            code, status = 126, "invalid_output"
            break
        if path.is_file() and path.name != "receipt.json":
            size = path.stat().st_size
            total += size
            files[path.relative_to(RESULT).as_posix()] = {"sha256": sha(path), "bytes": size}
    if total > 4 * 1024 * 1024:
        status, code = "output_limit", 125
    manifest = json.loads((ROOT / "job.json").read_text("utf-8"))
    receipt = {
        "version": 1, "id": manifest["id"], "kind": manifest["kind"],
        "status": status, "exit_code": code, "seconds": round(time.monotonic()-started, 4),
        "commit": os.environ.get("GITHUB_SHA", "local-test"),
        "source_sha256": sha(src),
        "files": files,
    }
    (RESULT / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print("RESULT_RECEIPT=" + json.dumps(receipt, sort_keys=True))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
