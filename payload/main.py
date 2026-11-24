"""Public numerical integration smoke test for the NumPy/SciPy profile."""
import json
from pathlib import Path
import numpy as np
from scipy.integrate import quad

value, error = quad(lambda x: np.sin(x), 0.0, float(np.pi))
result = {"integral_sin_0_pi": float(value), "estimated_error": float(error)}
assert abs(value - 2.0) < 1e-10
Path("result").mkdir(exist_ok=True)
Path("result/data.json").write_text(json.dumps(result, sort_keys=True) + "\n")
print(json.dumps(result, sort_keys=True))
