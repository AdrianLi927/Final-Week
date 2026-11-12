"""Tests for mechanics.py. Run from the project folder with: python -m pytest."""

import numpy as np
import pytest

import given
import mechanics
import numpy.typing as t

TINY = "data/tiny.zarr"
TINY_CSV_SUFFIX = "_si.csv"

# HELPER FUNCTIONS

def smooth_young_modulus(strain_pct: t.NDArray, stress_pa: t.NDArray, width_points: float = 45.0) -> float:
   smoothed_stress_pa = mechanics.smooth(stress_pa, width_points)
   return mechanics.young_modulus(strain_pct, smoothed_stress_pa)

def load_tiny_experiment_zarr(id: str):
   """
   Args:
      id (str): T01, T02 ect, does not support ids from gels.zarr

   Returns:
      dict: The returned record contains ``experiment_id``, ``type``, ``force_n``,
    ``area_m2``, and ``strain``. ``type`` is the experiment's category label
    from the Zarr group metadata (for example, ``"gel A"`` or ``"gel B"``);
    it is distinct from the machine label. The three measurement values are
    NumPy arrays; strain remains a dimensionless fraction.
   """
   return mechanics.load_experiment(TINY, id)

def load_tiny_experiment_csv(id: str):
   """
   Args:
      id (str): T01, T02 ect, does not support ids from gels.zarr
   """
   return given.read_table(f"data/{id}{TINY_CSV_SUFFIX}")

def run_tiny_pipeline(width_points: float = 0.0):
   return mechanics.run_pipeline(TINY, width_points)


def strain_pct_samples() -> t.NDArray[np.float64]:
    """Return strain from 0 to 20%, in 0.1% increments."""
    return np.arange(201, dtype=float) * 0.1


def bending_stress_pa(
    strain_pct: t.NDArray[np.float64], young_modulus_pa: float
) -> t.NDArray[np.float64]:
    """Bend near the ends while retaining a known linear fit region."""
    stress_pa = young_modulus_pa * strain_pct / 100

    low_strain = strain_pct < 1
    stress_pa[low_strain] += (
        young_modulus_pa
        * 0.01
        * (strain_pct[low_strain] / 1)
        * (1 - strain_pct[low_strain] / 1)
    )

    high_strain = strain_pct > 19
    stress_pa[high_strain] += (
        young_modulus_pa * 0.01 * ((strain_pct[high_strain] - 19) / 1) ** 2
    )
    return stress_pa


# TESTS
# PROMPT (final version used): 
# add pytest tests for some functions in mechanics.py

# a few tests will use the provided smooth_young_modulus. it takes in a np array of float for strain as % (note that all stress must start from 0 and only icnrease in increments of 0.1%) then stress as Pa (also np array of float), and finally just use the default val for width_points. It returns E in SI units (internally converts to fractions before doing E calculation). maybe create a helper for creating the strain_pct arrays

# the tests:

# E for a straight line: input data with an expected E value and see if the provided `smooth_young_modulus` function produces the expected output

# E for a curve: it bends now, see if it still gets the expected output

# E on a noisy curve: add noise to the data with curves

# E on a breaking noisy curve: the stress would suddenly jump (only decrease, since thats how materials work) and never reach a second maximum

# for all the above you would be generating your own data set (or writing code that generates that data set).

# for the rest of the tests below, you will compare the zarr stores from data/tiny.zarr to data/Txx.csv

# the data for the same id (T01, T02, T03, ignore gels.zarr) can be taken by:
# - tiny.zarr: data/tiny.zarr/[id] - read with `load_tiny_experiment_zarr`, returns SI units as defined in the docstring
# - csv: data/[[id]+"_si.csv"] - read with `load_tiny_experiment_csv`, its in a different format, check the "given" module and the csv files to see how they are structured.

# now for the specific tests:
# you will test if the data loaded from the zarr and csv for T01 and T02 are exactly the same

# as for the final type of test, you will use `run_tiny_pipeline` (again use default width_points) on tiny.zarr to check against an expected value (gel A 5370 Pa; gel B (9500 + 10100) / 2 = 9800 Pa, n = 2)

# all above tests have a specific tolerance for passing, you can look them up from `FINAL.md:138-146`

# dont worry if anything doesn't pass, thats a later problem, just write the tests for now.

# UNDER NO CIRCUMSTANCES SHOULD YOU INSPECT `mechanics.py` AT ANY TIME

# ask many questions and make no mistakes

def test_E_on_a_straight_line():
    """A constructed straight line has E=100000 Pa (pytest.approx rel=1e-6)."""
    expected_E_pa = 100_000.0
    strain_pct = strain_pct_samples()
    stress_pa = expected_E_pa * strain_pct / 100

    assert smooth_young_modulus(strain_pct, stress_pa, width_points=0) == pytest.approx(
        expected_E_pa, rel=1e-6
    )


def test_E_on_a_bending_curve():
    """The constructed curve is linear in its fit region, with E=100000 Pa (rel=1e-6)."""
    expected_E_pa = 100_000.0
    strain_pct = strain_pct_samples()
    stress_pa = bending_stress_pa(strain_pct, expected_E_pa)

    assert smooth_young_modulus(strain_pct, stress_pa, width_points=0) == pytest.approx(
        expected_E_pa, rel=1e-6
    )


def test_E_on_a_noisy_curve():
    """Seeded noise on the bending curve retains E=100000 Pa within 5%."""
    expected_E_pa = 100_000.0
    strain_pct = strain_pct_samples()
    stress_pa = bending_stress_pa(strain_pct, expected_E_pa)
    noise = np.random.default_rng(42).normal(
        loc=0.0, scale=expected_E_pa * 0.01, size=strain_pct.size
    )
    noise[0] = 0.0
    stress_pa += noise

    assert smooth_young_modulus(strain_pct, stress_pa) == pytest.approx(
        expected_E_pa, rel=0.05
    )


def test_E_on_a_breaking_noisy_curve():
    """A noisy curve with one drop and no later recovery to its peak has E=100000 Pa (rel=1e-6)."""
    expected_E_pa = 100_000.0
    strain_pct = strain_pct_samples()
    stress_pa = bending_stress_pa(strain_pct, expected_E_pa)
    break_index = np.flatnonzero(strain_pct >= 19)[0]
    peak_before_break = stress_pa[break_index - 1]
    post_break_noise = np.random.default_rng(43).normal(
        loc=0.0, scale=expected_E_pa * 0.005, size=strain_pct[break_index:].size
    )
    stress_pa[break_index:] = 0.35 * peak_before_break + post_break_noise
    stress_pa[0] = 0.0

    assert smooth_young_modulus(strain_pct, stress_pa, width_points=0) == pytest.approx(
        expected_E_pa, rel=1e-6
    )


@pytest.mark.parametrize("experiment_id", ["T01", "T02"])
def test_tiny_zarr_matches_csv(experiment_id: str):
    """The zarr force, area, and strain match the SI CSV values (rel=1e-6)."""
    zarr_experiment = load_tiny_experiment_zarr(experiment_id)
    csv_experiment = load_tiny_experiment_csv(experiment_id)

    assert zarr_experiment["force_n"] == pytest.approx(
        csv_experiment["force_N"], rel=1e-6
    )
    assert zarr_experiment["area_m2"] == pytest.approx(
        csv_experiment["area_m2"], rel=1e-6
    )
    assert zarr_experiment["strain"] == pytest.approx(
        csv_experiment["strain"], rel=1e-6
    )


def test_tiny_pipeline_matches_expected_gel_moduli():
    """tiny.zarr yields gel A=5370 Pa and gel B=9800 Pa (rel=1%); gel B has n=2."""
    summary = run_tiny_pipeline()

    assert summary["gel A"]["mean_E_pa"] == pytest.approx(5370, rel=0.01)
    assert summary["gel B"]["mean_E_pa"] == pytest.approx(9800, rel=0.01)
    assert summary["gel B"]["n"] == 2
