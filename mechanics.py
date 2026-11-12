"""Final exercise: Young's modulus of four hydrogels. Definitions only: importing this file prints nothing.

Five required functions have names and parameters fixed (see FINAL.md). A
public region-selection function supports plotting the modulus range. Above
each required function, the final prompt is preserved in its # PROMPT block;
under the signature is the implemented body.
"""

import zarr
import numpy as np


from typing import no_type_check


_FORCE_UNIT_TO_N = {"N": 1.0, "mN": 1e-3}
_AREA_UNIT_TO_M2 = {"m^2": 1.0, "cm^2": 1e-4, "mm^2": 1e-6}

_STRESS_READING_INTERVAL_PCT = 0.1 # constant % strain apart that each stress reading is read, saw from the csv that this seems constant


# PROMPT (final version used):
# Write function `def load_experiment(store_path: str, experiment_id: str) -> list[tuple[float, float, float]]:` in `mechanics.py` that fits the docstring below:

# """
# loads an experiment from either machines A and B, from a .zarr store path, and returns a list of tuples in SI units

# store_path: str - path to the .zarr store

# experiment_id: str - the experiment id, e.g. "G71", "T03"

# returns: list[tuple[float(strain: %), float(stress: Pa), float(area: m^2)]]
# """

# Using zarr3 and inspecting the current zarr structure in `data/tiny.zarr`, you will access the experiment data and parse it into the data format specified above.

# Note that there the experiment data can be from machines A or B, and units from the same machine can be different, so add placeholder unit conversion tables on top of the function (for the few you find in `tiny.zarr`) and I will add more conversions as needed

# Ask many questions and make no mistakes

@no_type_check
def load_experiment(store_path: str, experiment_id: str) -> dict:
    """
    Load one experiment and convert its measurements to the common SI format.

    The returned record contains ``experiment_id``, ``type``, ``force_n``,
    ``area_m2``, and ``strain``. ``type`` is the experiment's category label
    from the Zarr group metadata (for example, ``"gel A"`` or ``"gel B"``);
    it is distinct from the machine label. The three measurement values are
    NumPy arrays; strain remains a dimensionless fraction.

    Args:
        store_path: Path to the Zarr v3 store.
        experiment_id: Experiment group name, such as ``"G71"`` or ``"T03"``.
    """

    root = zarr.open_group(store_path, mode="r")
    if experiment_id not in root:
        raise KeyError(f"Experiment {experiment_id!r} not found in {store_path!r}")

    experiment = root[experiment_id]
    data_array = experiment["data"]
    values = data_array[:]
    attributes = data_array.attrs
    columns = attributes["columns"]
    column_index = {name: index for index, name in enumerate(columns)}
    required_columns = {"force", "area", "strain"}
    if not required_columns.issubset(column_index):
        raise ValueError(
            f"Experiment {experiment_id!r} must contain force, area, and strain columns"
        )

    machine = experiment.attrs["machine"]

    if machine == "A":
        try:
            force_scale = _FORCE_UNIT_TO_N[attributes["force_unit"]]
        except KeyError as error:
            raise ValueError(
                f"Unsupported force unit {error.args[0]!r} for experiment "
                f"{experiment_id!r}"
            ) from error
        try:
            area_scale = _AREA_UNIT_TO_M2[attributes["area_unit"]]
        except KeyError as error:
            raise ValueError(
                f"Unsupported area unit {error.args[0]!r} for experiment "
                f"{experiment_id!r}"
            ) from error
    elif machine == "B":
        try:
            force_scale = 10.0 ** attributes["force_exp"]
            area_scale = 10.0 ** attributes["area_exp"]
        except KeyError as error:
            raise ValueError(
                f"Missing unit exponent {error.args[0]!r} for experiment "
                f"{experiment_id!r}"
            ) from error
    else:
        raise ValueError(
            f"Unsupported machine {machine!r} for experiment {experiment_id!r}"
        )


    return {
        "experiment_id": experiment_id,
        "type": experiment.attrs["type"],
        "force_n": values[:, column_index["force"]] * force_scale,
        "area_m2": values[:, column_index["area"]] * area_scale,
        "strain": values[:, column_index["strain"]],
    }


# PROMPT (final version used):
# implement `def stress_strain(record: dict) -> dict:` where record is the return value of `load_experiment`

# this function maps the previous record into strain (from a fraction to %) and pressure in Pa

# write a docstring of similar scope to that of `load_experiment`

# ask many questions and make no mistakes
def stress_strain(experiment_record: dict) -> dict:
    """
    Convert a loaded experiment record to strain percent and stress in pascals.

    The record is the dictionary returned by ``load_experiment``. Its
    ``strain`` values are dimensionless fractions, and ``force_n`` and
    ``area_m2`` are NumPy arrays in SI units.

    Returns a dictionary containing ``strain_pct`` and ``stress_pa`` as
    NumPy arrays.
    """
    return {
        "strain_pct": experiment_record["strain"] * 100,
        "stress_pa": experiment_record["force_n"] / experiment_record["area_m2"],
    }


# PROMPT (final version used):
# implement `def smooth(stress_pa: [numpy array with floats as returned from the return from stress_strain], width_points: float):`

# this will modify the provided stress array

# each stress reading is read every `_STRESS_READING_INTERVAL_PCT`

# the smoothened array will be a weighted moving average with the window equal to `width_points` (in units % strain) and weighted with a normal distribution, for now make the strength of the window (the weight of the distribution at the edge of the window) a constant variable on top of the function

# write a docstring of similar scope to that of `load_experiment`

# ask many questions and make no mistakes
def smooth(stress_pa: np.ndarray, width_points: float) -> np.ndarray:
    """
    Smooth a stress curve in place with a Gaussian-weighted moving average.

    The one-dimensional stress array is sampled every
    ``_STRESS_READING_INTERVAL_PCT`` percent strain. ``width_points`` is the
    full window width in sample points, converted to percent strain using
    that sampling interval; samples no farther than half that width from
    each center are included. The Gaussian weight at each window edge is
    0.1 relative to the center weight. Samples outside the window are
    excluded.
    Near either end of the curve, only available samples are used and their
    weights are renormalized.

    Args:
        stress_pa: NumPy array of stress values in pascals. The array is
            modified in place.
        width_points: Full moving-window width in sample points. For example,
            10 points span 1% strain with the current sampling interval.
            Zero leaves the array unchanged.

    Returns:
        The same ``stress_pa`` array after smoothing.

    Raises:
        ValueError: If ``width_points`` is negative or not finite.
    """
    if not np.isfinite(width_points) or width_points < 0:
        raise ValueError("width_points must be a finite non-negative number")
    if width_points == 0 or stress_pa.size == 0:
        return stress_pa

    window_width_pct = width_points * _STRESS_READING_INTERVAL_PCT
    half_window_pct = window_width_pct / 2.0
    max_available_offset = stress_pa.size - 1
    if half_window_pct >= max_available_offset * _STRESS_READING_INTERVAL_PCT:
        max_offset = max_available_offset
    else:
        offsets_in_readings = half_window_pct / _STRESS_READING_INTERVAL_PCT
        max_offset = int(np.floor(np.nextafter(offsets_in_readings, np.inf)))
    if max_offset == 0:
        return stress_pa

    sigma_pct = half_window_pct / np.sqrt(-2.0 * np.log(0.1))
    offsets = np.arange(-max_offset, max_offset + 1)
    weights = np.exp(
        -0.5
        * ((offsets * _STRESS_READING_INTERVAL_PCT) / sigma_pct) ** 2
    )

    original_stress = stress_pa.copy()
    for center in range(stress_pa.size):
        start = max(0, center - max_offset)
        stop = min(stress_pa.size, center + max_offset + 1)
        kernel_start = start - center + max_offset
        kernel_stop = stop - center + max_offset
        local_weights = weights[kernel_start:kernel_stop]
        stress_pa[center] = (
            np.dot(original_stress[start:stop], local_weights)
            / local_weights.sum()
        )

    return stress_pa


def _young_modulus_region(
    strain_pct: np.ndarray, smoothened_stress_pa: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, int, int]:
    try:
        strain = np.asarray(strain_pct, dtype=float)
        stress = np.asarray(smoothened_stress_pa, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError("strain and stress must contain numeric values") from error

    if strain.ndim != 1 or stress.ndim != 1:
        raise ValueError("strain and stress must be one-dimensional arrays")
    if strain.size == 0 or strain.size != stress.size:
        raise ValueError("strain and stress must be non-empty arrays of equal length")
    if not np.all(np.isfinite(strain)) or not np.all(np.isfinite(stress)):
        raise ValueError("strain and stress values must all be finite")

    maximum_stress = np.max(stress)
    if maximum_stress <= 0:
        raise ValueError("maximum stress must be positive")

    peak_index = int(np.argmax(stress))
    threshold_15_pa = 0.15 * maximum_stress
    threshold_85_pa = 0.85 * maximum_stress
    pre_peak_stress = stress[: peak_index + 1]
    threshold_15_index = int(np.argmin(np.abs(pre_peak_stress - threshold_15_pa)))
    threshold_85_index = int(np.argmin(np.abs(pre_peak_stress - threshold_85_pa)))
    selected = (
        (np.arange(stress.size) <= peak_index)
        & (stress >= threshold_15_pa)
        & (stress <= threshold_85_pa)
    )
    selected_strain = strain[selected]
    if selected_strain.size < 2 or np.ptp(selected_strain) == 0:
        raise ValueError(
            r"the 15%-85% stress region must contain two distinct strain values"
        )

    return (
        strain,
        stress,
        selected,
        maximum_stress,
        threshold_15_index,
        threshold_85_index,
    )


def young_modulus_region(
    strain_pct: np.ndarray, smoothened_stress_pa: np.ndarray
) -> dict:
    """Return the samples and threshold locations used for Young's modulus.

    Threshold sample indices are the samples at or before the peak whose
    smoothed stress is closest to 15% and 85% of the maximum, respectively.
    The selected mask matches the inclusive 15%-85% region used by
    :func:`young_modulus`.
    """
    (
        _,
        _,
        selected,
        maximum_stress,
        threshold_15_index,
        threshold_85_index,
    ) = _young_modulus_region(strain_pct, smoothened_stress_pa)
    return {
        "selected_mask": selected,
        "threshold_15_pa": 0.15 * maximum_stress,
        "threshold_15_index": threshold_15_index,
        "threshold_85_pa": 0.85 * maximum_stress,
        "threshold_85_index": threshold_85_index,
    }

# PROMPT (final version used):
# write function `def young_modulus(strain_pct: np.ndarray, smoothened_stress_pa: np.ndarray) -> float:`

# the function will take in `strain_pct` (from func `stress_strain`) and smoothened_stress_pa (from func `smooth`) and return a single youngs modulus E

# E in our case is defined by the gradient of the data between 85% and 15% of the maximum stress, where strain values higher than where the maximum stress is, are ignored for the gradient calculation

# maximum stress is just the maximum value of the smoothened data

# write a docstring of similar scope to that of `load_experiment`

# ask many questions and make no mistakes
def young_modulus(strain_pct: np.ndarray, smoothened_stress_pa: np.ndarray) -> float:
    """
    Calculate Young's modulus from the specified portion of a stress-strain curve.

    The stress maximum is the maximum value in ``smoothened_stress_pa``. The
    linear-fit region includes samples at or before the first occurrence of
    that maximum whose stress is inclusively between 15% and 85% of the
    maximum. The selected strain values are converted from percent to
    dimensionless fractions before fitting. The returned value is the
    least-squares slope of stress (Pa) against dimensionless strain, in Pa.

    Args:
        strain_pct: One-dimensional array of strain values in percent.
        smoothened_stress_pa: Matching one-dimensional array of smoothed stress
            values in pascals.

    Returns:
        Young's modulus in pascals, calculated as the stress-versus-strain
        slope for the selected region.

    Raises:
        ValueError: If the arrays are empty, not one-dimensional, have
            different lengths, contain non-finite values, have a non-positive
            maximum stress, or do not provide two selected samples with
            distinct strain values.
    """
    strain, stress, selected, _, _, _ = _young_modulus_region(
        strain_pct, smoothened_stress_pa
    )
    selected_strain = strain[selected]
    selected_stress = stress[selected]

    selected_strain_fraction = selected_strain / 100.0
    centered_strain = selected_strain_fraction - np.mean(selected_strain_fraction)
    centered_stress = selected_stress - np.mean(selected_stress)
    return float(
        np.dot(centered_strain, centered_stress)
        / np.dot(centered_strain, centered_strain)
    )


# PROMPT (final version used):
# finish function `def run_pipeline(store_path: str, width_points: float):`

# store_path is a path to a zarr store (like data/tiny.zarr or data/gels.zarr). there will be an attribute inside each experiment log store/Gxx (or store/Txx for tiny.zarr) called type (gel A, gel B ect)

# this function should loop over experiment ids (G01, G02) in alphabetical order (whatever implementation is easiest), and calculate the values below for them, and returning a dictionary keyed by gel type (keys being exactly gel A, gel B ect)

# this will get the mean young's modulus, standard deviation (numpy.std with ddof=1), and number of entries for that specific gel

# you should run the prewritten `def get_young_modulus_for_id(id: str) -> float:` function that I wrote to obtain youngs modulus for a specific experiment id though check if it makes sense

# write a docstring of similar scope to that of `load_experiment`

# ask many questions and make no mistakes
def run_pipeline(store_path: str, width_points: float):
    """
    Calculate Young's modulus summaries for each experiment type in a Zarr store.

    Experiments are processed in alphabetical order by ID. Each experiment's
    type comes from its group attributes, and its modulus is calculated by the
    nested ``_get_young_modulus_for_id`` helper. Summary values are grouped by
    type and returned in alphabetical order.

    Args:
        store_path: Path to the Zarr v3 store.
        width_points: Full smoothing-window width in sample points. Each point
            spans ``_STRESS_READING_INTERVAL_PCT`` percent strain.

    Returns:
        A dictionary keyed by experiment type. Each value contains
        ``mean_E_pa``, ``sd_E_pa`` (sample standard deviation with ``ddof=1``),
        and ``n`` (the number of experiments of that type).
    """
    def _get_young_modulus_for_id(id: str) -> float:
        experiment_data = load_experiment(store_path, id)
        stress_strain_data = stress_strain(experiment_data)
        smooth(stress_strain_data["stress_pa"], width_points)

        return young_modulus(
            stress_strain_data["strain_pct"], stress_strain_data["stress_pa"]
        )

    root = zarr.open_group(store_path, mode="r")
    modulus_by_type = {}
    for experiment_id in sorted(root.group_keys()):
        experiment_type = root[experiment_id].attrs["type"]
        modulus_by_type.setdefault(experiment_type, []).append(
            _get_young_modulus_for_id(experiment_id)
        )

    return {
        experiment_type: {
            "mean_E_pa": float(np.mean(moduli)),
            "sd_E_pa": float(np.std(moduli, ddof=1)),
            "n": len(moduli),
        }
        for experiment_type, moduli in sorted(modulus_by_type.items())
    }
