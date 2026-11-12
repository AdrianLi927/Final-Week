"""Find the smoothing width that maximizes mean Young's modulus per gel type.

Run from the project folder with: python find_optimal_width.py
"""
import matplotlib.pyplot as plt
import mechanics


STORE = "data/gels.zarr"
MIN_WIDTH = 0
MAX_WIDTH = 70


def main() -> None:
    results_by_type: dict[str, list[tuple[int, float, float, int]]] = {}

    for width in range(MIN_WIDTH, MAX_WIDTH + 1):
        print(f"Running pipeline for width {width}")
        summary = mechanics.run_pipeline(STORE, width)
        for gel_type, result in summary.items():
            results_by_type.setdefault(gel_type, []).append(
                (width, result["mean_E_pa"], result["sd_E_pa"], result["n"])
            )
            
    print("Plotting Graph...")

    figure, axis = plt.subplots()
    for gel_type, results in sorted(results_by_type.items()):
        widths = [width for width, _, _, _ in results]
        means_kpa = [mean_pa / 1000 for _, mean_pa, _, _ in results]
        mean_line, = axis.plot(
            widths, means_kpa, marker="o", markersize=3, label=f"{gel_type} mean E"
        )
        standard_deviations_kpa = [
            sd_pa / 1000 for _, _, sd_pa, _ in results
        ]
        axis.plot(
            widths,
            standard_deviations_kpa,
            linestyle="--",
            color=mean_line.get_color(),
            label=f"{gel_type} SD",
        )

        max_mean_pa = max(mean_pa for _, mean_pa, _, _ in results)
        best_results = [
            (width, sd_pa)
            for width, mean_pa, sd_pa, _ in results
            if mean_pa == max_mean_pa
        ]
        sample_count = results[0][3]
        best_options = ", ".join(
            f"{width} points ({width / 10:.1f}% strain; "
            f"SD {sd_pa / 1000:.2f} kPa)"
            for width, sd_pa in best_results
        )
        print(
            f"{gel_type}: maximum mean E = {max_mean_pa / 1000:.2f} kPa "
            f"at {best_options}, "
            f"n = {sample_count}"
        )

    axis.set_xlabel("Smoothing width (points)")
    axis.set_ylabel("Mean Young's modulus (kPa)")
    axis.set_title("Mean Young's modulus by gel type and smoothing width")
    axis.legend(title="Gel type")
    axis.grid(True)
    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
