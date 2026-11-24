#!/usr/bin/env python3
"""Conservative syntax guard; not a substitute for the Lean kernel."""
from pathlib import Path
import re
import sys
if len(sys.argv) != 2 or not sys.argv[1].startswith("profiles/lean-"):
    raise SystemExit("Expected a proof source under profiles/lean-*")
source = Path(sys.argv[1]).read_text("utf-8")
if re.search(r"\b(?:sorry|admit|axiom|native_decide|unsafe)\b", source):
    raise SystemExit("UNVERIFIED_PROOF_SOURCE")
print("SOURCE_POLICY_OK")
