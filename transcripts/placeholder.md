Write function `def load_experiment(store_path: str, experiment_id: str) -> dict[float, float]:` that fits the docstring below:

"""
loads an experiment from either machines A and B, from a .zarr store path, and returns a dictionary in SI units

store_path: str - path to the .zarr store

experiment_id: str - the experiment id, e.g. "G71", "T03"

returns: list[set[float(strain %), float(stress pascals), float(area m^2)]]
"""

Using zarr3 and inspecting the current zarr structure in `data/tiny.zarr`, you will access the experiment data and parse it into the data format specified above.

Note that there the experiment data can be from machines A or B