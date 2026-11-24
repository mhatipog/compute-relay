#!/usr/bin/env python3
"""Portable LAMMPS CPU smoke test with an analytical energy/force check."""
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

PAIR = """units lj
atom_style atomic
boundary p p p
region box block 0 10 0 10 0 10 units box
create_box 1 box
create_atoms 1 single 4 5 5 units box
create_atoms 1 single 5.5 5 5 units box
mass 1 1.0
pair_style lj/cut 2.5
pair_coeff 1 1 1.0 1.0 2.5
thermo_modify norm no
run 0
print "PAIR_PE=$(pe:%.16g)"
group first id 1
compute force first reduce sum fx
run 0
print "PAIR_FX=$(c_force:%.16g)"
"""
NVE = """units lj
atom_style atomic
boundary p p p
lattice fcc 0.8
region box block 0 3 0 3 0 3
create_box 1 box
create_atoms 1 box
mass 1 1
pair_style lj/cut 2.5
pair_coeff 1 1 1.0 1.0 2.5
pair_modify shift yes
velocity all create 0.7 394817 mom yes rot no dist gaussian
timestep 0.001
fix integrator all nve
thermo 100
thermo_style custom step atoms temp pe ke etotal
thermo_modify norm no
run 0
print "INITIAL=$(etotal:%.16g)"
run 500
print "FINAL=$(etotal:%.16g)"
print "ATOMS=$(atoms:%.0f)"
"""
def sha(data):
    return hashlib.sha256(data).hexdigest()

def invoke(exe, source, root, name):
    path = root / (name + ".in")
    path.write_text(source)
    proc = subprocess.run([exe, "-in", str(path), "-log", "none"],
                          cwd=root, stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True,
                          timeout=90, env={**os.environ, "OMP_NUM_THREADS": "1"})
    if proc.returncode:
        raise RuntimeError(proc.stdout[-12000:])
    return proc.stdout

def value(log, key):
    matches = re.findall(r"^" + re.escape(key) + r"=([-+0-9.eE]+)\s*$",
                         log, re.M)
    if len(matches) != 1:
        raise ValueError(f"missing/duplicate {key}")
    x = float(matches[0])
    if not math.isfinite(x):
        raise ValueError(f"nonfinite {key}")
    return x

def main():
    exe = shutil.which("lmp") or shutil.which("lammps")
    if not exe:
        raise SystemExit("LAMMPS executable not installed")
    exe = str(Path(exe).resolve())
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        pair = invoke(exe, PAIR, root, "pair")
        nve = invoke(exe, NVE, root, "nve")
    r = 1.5
    energy_expected = 4*(r**-12-r**-6)
    force_expected = 24*(r**-7-2*r**-13)
    energy, force = value(pair,"PAIR_PE"), value(pair,"PAIR_FX")
    initial, final = value(nve,"INITIAL"), value(nve,"FINAL")
    atoms = value(nve,"ATOMS")
    drift = abs(final-initial)/atoms
    if abs(energy-energy_expected)>1e-9 or abs(force-force_expected)>1e-9:
        raise RuntimeError("Lennard-Jones reference check failed")
    if atoms != 108 or drift>0.01:
        raise RuntimeError(f"NVE smoke check failed: {atoms=} {drift=}")
    receipt = {"status":"passed","scope":"generic engine smoke only",
        "engine_banner":pair.splitlines()[0],
        "binary_sha256":sha(Path(exe).read_bytes()),
        "script_sha256":sha(Path(__file__).read_bytes()),
        "input_sha256":{"pair":sha(PAIR.encode()),"nve":sha(NVE.encode())},
        "output_sha256":{"pair":sha(pair.encode()),"nve":sha(nve.encode())},
        "pair":{"energy":energy,"expected_energy":energy_expected,
                "force_x":force,"expected_force_x":force_expected},
        "nve":{"atoms":int(atoms),"steps":500,"initial":initial,"final":final,
               "energy_drift_per_atom":drift},
        "commit":os.environ.get("GITHUB_SHA","local")}
    print(json.dumps(receipt,sort_keys=True))
if __name__=="__main__":
    main()
