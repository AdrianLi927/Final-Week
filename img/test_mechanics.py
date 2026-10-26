"""Tests for mechanics.py. Run from the project folder with:  python -m pytest

How to build this file (as in weeks 4 and 5):
  1. You write the test names and the docstrings. Each docstring says what is
     checked and the EXPECTED VALUE, with its source (a curve you built, so
     known by construction; a _si.csv export; a table in FINAL.md).
  2. Every body starts as  assert False, "body not written yet"  so the suite
     is red until it is filled in (an empty body would pass).
  3. The bodies come from an assistant in a SEPARATE chat that never sees
     mechanics.py. Its prompt goes in the # PROMPT block below.
  4. Decimals are compared with pytest.approx, never with ==.

At least seven tests: four on the curves you build (FINAL.md, "Your digital
data"), two on the loader (one for each machine), one on the pipeline.

given.read_table(path) reads any of the CSV files in data/ into a dictionary
{column name: numpy array}, e.g. given.read_table("data/T01_si.csv") has the
keys "strain", "force_N" and "area_m2".
"""
# PROMPT (final version used):
# ...
import pytest

import given
import mechanics

TINY = "data/tiny.zarr"


def test_E_on_a_straight_line():
    """An example of the format. A straight line I built: strain 0 to 20 % every
    0.1 %, stress = 10 000 Pa x strain (as a fraction). With width 0, E is
    10 000 Pa, by construction (to 1e-6)."""
    assert False, "body not written yet"
