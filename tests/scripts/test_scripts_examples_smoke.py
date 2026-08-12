"""Smoke coverage for ``Scripts/Examples`` — currently MISSING from the suite.

``tests/models/test_documentation_models.py`` runpy-runs ``library/models`` and
keeps them green, but nothing runs ``Scripts/Examples``. As a result five of
those scripts silently broke against the 0.19 API (see jonhanke-nam/PsyNeuLink#31)
— each fails at construction/import, standalone, before any run:

  _Gating-Mechanism.py                  line 59  ValueError: input operand has more dimensions...
  _Reinforcement-Learning REV.py        line 36  ParameterError: 'value' is read-only
  LC Control Mechanism Composition.py   line 23  ParameterError: 'value' is read-only
  Gilbert_Shallice_Composition_Model.py line 18  ComponentError: Variable format ([-6]) ...
  Mixed-NN-and-DDM.py                   line 30  AttributeError: no attribute 'get_matrix'

This file is the missing coverage. The known-broken scripts are xfail(strict) so
the suite is green today and flips loudly when a script is fixed — then move it
out of BROKEN. Extend to the full corpus once the five are repaired.
"""
import pathlib
import runpy
import sys

import matplotlib
matplotlib.use("Agg")  # never open a plot window during the test
import pytest

EXAMPLES = pathlib.Path(__file__).resolve().parents[2] / "Scripts" / "Examples"

BROKEN = {
    "_Gating-Mechanism.py": "line 59 ValueError: more dimensions (proj matrix vs 0.19)",
    "_Reinforcement-Learning REV.py": "line 36 ParameterError: 'value' is read-only",
    "LC Control Mechanism Composition.py": "line 23 ParameterError: 'value' is read-only",
    "Gilbert_Shallice_Composition_Model.py": "line 18 ComponentError: Variable format ([-6])",
    "Mixed-NN-and-DDM.py": "line 30 AttributeError: no attribute 'get_matrix'",
}


@pytest.mark.parametrize(
    "fname",
    [pytest.param(f, marks=pytest.mark.xfail(reason=r, strict=True)) for f, r in BROKEN.items()],
)
def test_scripts_example_runs(fname):
    """Each Scripts/Examples model should at least construct + run via runpy."""
    path = EXAMPLES / fname
    assert path.exists(), f"missing example: {path}"
    sys.argv = [str(path)]  # neutralize the scripts' argparse
    runpy.run_path(str(path), run_name="__main__")
