"""Public, neutral execution smoke test."""
from math import factorial
from pathlib import Path
import json
Path("result").mkdir(exist_ok=True)
value = factorial(12)
Path("result/data.json").write_text(json.dumps({"factorial_12": value}) + "\n")
print(value)
