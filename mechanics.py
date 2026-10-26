"""Final exercise: Young's modulus of four hydrogels. Definitions only: importing this file prints nothing.

Five separate functions, names and parameters fixed (see FINAL.md). Above each
one, your final prompt, verbatim, in its # PROMPT block; under the signature,
the body that came back. Earlier attempts stay in the transcript.
"""


# PROMPT (final version used):
# ...
def load_experiment(store_path: str, experiment_id: str) -> list[set[float, float, float]]:
    """
    loads an experiment from either machines A and B, from a .zarr store path, and returns a dictionary in SI units

    store_path: str - path to the .zarr store

    experiment_id: str - the experiment id, e.g. "G71", "T03"

    returns: list[set[float(strain %), float(stress pascals), float(area m^2)]]
    """

    raise NotImplementedError("load_experiment: not written yet")


# PROMPT (final version used):
# ...
def stress_strain(record):
    raise NotImplementedError("stress_strain: not written yet")


# PROMPT (final version used):
# ...
def smooth(stress_pa, width_points):
    raise NotImplementedError("smooth: not written yet")


# PROMPT (final version used):
# ...
def young_modulus(strain_pct, stress_pa):
    raise NotImplementedError("young_modulus: not written yet")


# PROMPT (final version used):
# ...
def run_pipeline(store_path, width_points):
    raise NotImplementedError("run_pipeline: not written yet")
