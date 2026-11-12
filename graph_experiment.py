# I made this to find a nice looking width_points

# PROMPT (final version used):
# add a test in test_mechanics.py for showing a matplotlib graph of a single experiment id in data/gels.zarr, I will put the experiment id in later, along with the smoothen window width, leave it as a placeholder for now

# use the preexisting functions in mechanics.py to plot the stress/strain graph of the raw experiment data, then plots of a different color to show the smoothened data

import matplotlib.pyplot as plt
import numpy as np
import pytest
import mechanics

STORE_PATH = "data/gels.zarr"
GELS_EXPERIMENT_ID = "G14"
SMOOTHING_WINDOW_WIDTH_POINTS = 24 # same units as in main.py, *10 to get strain pct
SMOOTHING_WINDOW_WIDTH_POINTS_2 = None

def test_young_modulus_region_reports_selected_samples_and_thresholds():
    strain_pct = [0, 1, 2, 3, 4, 5]
    stress_pa = [0, 15, 50, 85, 100, 60]

    region = mechanics.young_modulus_region(strain_pct, stress_pa)

    assert region["selected_mask"].tolist() == [
        False,
        True,
        True,
        True,
        False,
        False,
    ]
    assert region["threshold_15_index"] == 1
    assert region["threshold_85_index"] == 3
    assert region["threshold_15_pa"] == pytest.approx(15)
    assert region["threshold_85_pa"] == pytest.approx(85)


def test_plot_raw_and_smoothed_gels_experiment():
    """Display raw and smoothed stress-strain curves for one gels.zarr experiment."""
    if (
        GELS_EXPERIMENT_ID is None
        or SMOOTHING_WINDOW_WIDTH_POINTS is None
    ):
        pytest.skip(
            "Set GELS_EXPERIMENT_ID and SMOOTHING_WINDOW_WIDTH_POINTS first"
        )

    experiment = mechanics.load_experiment(STORE_PATH, GELS_EXPERIMENT_ID)
    curve = mechanics.stress_strain(experiment)
    smoothing_widths = [SMOOTHING_WINDOW_WIDTH_POINTS]
    if SMOOTHING_WINDOW_WIDTH_POINTS_2 is not None:
        smoothing_widths.append(SMOOTHING_WINDOW_WIDTH_POINTS_2)
    smoothed_curves = [
        mechanics.smooth(curve["stress_pa"].copy(), width)
        for width in smoothing_widths
    ]
    smoothed_stress_pa_1 = smoothed_curves[0]
    region = mechanics.young_modulus_region(curve["strain_pct"], smoothed_stress_pa_1)
    strain_reading_interval_pct = (
        curve["strain_pct"][1] - curve["strain_pct"][0]
    )
    window_widths_pct = tuple(
        width * strain_reading_interval_pct for width in smoothing_widths
    )
    selected_strain_pct = curve["strain_pct"][region["selected_mask"]]
    selected_stress_pa = smoothed_stress_pa_1[region["selected_mask"]]
    young_modulus_pa = mechanics.young_modulus(
        curve["strain_pct"], smoothed_stress_pa_1
    )
    fit_intercept_pa = selected_stress_pa.mean() - young_modulus_pa * (
        selected_strain_pct.mean() / 100
    )
    threshold_85_pa = region["threshold_85_pa"]
    threshold_15_pa = region["threshold_15_pa"]
    fit_start_strain_pct = (
        100 * (threshold_15_pa - fit_intercept_pa) / young_modulus_pa
    )
    fit_end_strain_pct = 100 * (threshold_85_pa - fit_intercept_pa) / young_modulus_pa
    fit_strain_pct = np.linspace(fit_start_strain_pct, fit_end_strain_pct, 100)

    figure, axis = plt.subplots()
    axis.scatter(
        curve["strain_pct"],
        curve["stress_pa"],
        color="black",
        alpha=0.8,
        label="Raw",
    )
    for width, smoothed_stress_pa, color in zip(
        smoothing_widths, smoothed_curves, ("tab:orange", "tab:cyan")
    ):
        axis.plot(
            curve["strain_pct"],
            smoothed_stress_pa,
            color=color,
            label=f"Smoothed ({width:g} points)",
        )
    axis.plot(
        fit_strain_pct,
        fit_intercept_pa + young_modulus_pa * fit_strain_pct / 100,
        color="tab:green",
        linestyle="--",
        label=f"E fit (E = {young_modulus_pa:.3g} Pa)",
    )
    threshold_85_strain_pct = curve["strain_pct"][region["threshold_85_index"]]
    for index, (width, width_pct, color) in enumerate(
        zip(smoothing_widths, window_widths_pct, ("tab:orange", "tab:cyan"))
    ):
        window_y = 0.96 - index * 0.06
        axis.annotate(
            "",
            xy=(threshold_85_strain_pct + width_pct / 2, window_y),
            xytext=(threshold_85_strain_pct - width_pct / 2, window_y),
            xycoords=axis.get_xaxis_transform(),
            arrowprops={"arrowstyle": "<->", "color": color, "linewidth": 2},
        )
        axis.text(
            threshold_85_strain_pct,
            window_y,
            f"Window: {width:g} points ({width_pct:g}% strain)",
            transform=axis.get_xaxis_transform(),
            horizontalalignment="center",
            verticalalignment="bottom",
            color=color,
        )
    axis.set_xlabel("Strain (%)")
    axis.set_ylabel("Stress (Pa)")
    axis.set_title(
        f"Experiment {GELS_EXPERIMENT_ID} - {experiment['type']}"
    )
    axis.legend()
    axis.grid(True)
    plt.show()
    plt.close(figure)

test_plot_raw_and_smoothed_gels_experiment()
