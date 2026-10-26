"""GIVEN: do not change this file. Definitions only: importing it prints nothing."""
import numpy as np


def read_table(path) -> dict:
    """Read a CSV file of numbers into a dictionary: column name -> numpy array.

    Lines starting with '#' are notes and are skipped; the first other line
    is the header with the column names; every line after it is one row of
    numbers separated by commas. Works for data/T0*_si.csv.
    """
    names = None
    rows = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            if names is None:
                names = line.split(",")
                continue
            rows.append([float(x) for x in line.split(",")])
    table = np.array(rows)
    return {name: table[:, i] for i, name in enumerate(names)}
