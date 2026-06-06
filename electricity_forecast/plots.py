from __future__ import annotations


def actual_vs_predicted_figure(df):
    from matplotlib.figure import Figure

    fig = Figure(figsize=_actual_vs_predicted_size(df), tight_layout=True)
    draw_actual_vs_predicted(fig, df)
    return fig


def draw_actual_vs_predicted(figure, df) -> None:
    import math

    areas = [] if df is None or df.empty else sorted(df["area"].dropna().unique())
    model_names = _model_names(df)
    model_colors = _model_color_map(model_names)
    cols = min(3, max(1, len(areas)))
    rows = max(1, math.ceil(max(len(areas), 1) / cols))
    figure.clear()
    axes = figure.subplots(rows, cols, squeeze=False)
    flat_axes = list(axes.ravel())
    if not areas:
        axis = flat_axes[0]
        axis.set_title("Actual vs Predicted")
        axis.set_xlabel("Actual kWh")
        axis.set_ylabel("Predicted kWh")
        axis.text(0.5, 0.5, "No backtest data", ha="center", va="center")
        for axis in flat_axes[1:]:
            axis.set_visible(False)
        return

    for axis, area in zip(flat_axes, areas):
        group = df[df["area"].eq(area)]
        actual = group["actual_kwh"].astype(float)
        predicted = group["predicted_kwh"].astype(float)
        min_value = min(float(actual.min()), float(predicted.min()))
        max_value = max(float(actual.max()), float(predicted.max()))
        pad = max((max_value - min_value) * 0.08, 1.0)
        if "model_name" in group.columns and len(model_names) > 1:
            model_labels = group["model_name"].astype(str)
            for model_name in model_names:
                model_group = group[model_labels.eq(model_name)]
                if model_group.empty:
                    continue
                axis.scatter(
                    model_group["actual_kwh"].astype(float),
                    model_group["predicted_kwh"].astype(float),
                    s=14,
                    color=model_colors.get(str(model_name), "#3158d4"),
                    alpha=0.62,
                    label=str(model_name),
                )
            axis.legend(loc="upper left", fontsize="x-small")
        else:
            axis.scatter(actual, predicted, s=14, color="#3158d4", alpha=0.65)
        axis.plot(
            [min_value - pad, max_value + pad],
            [min_value - pad, max_value + pad],
            linestyle="--",
            color="#d55e5e",
            linewidth=1.3,
        )
        axis.set_title(f"{area}: Actual vs Predicted")
        axis.set_xlabel("Actual kWh")
        axis.set_ylabel("Predicted kWh")
        axis.grid(True, alpha=0.2)
        axis.set_xlim(min_value - pad, max_value + pad)
        axis.set_ylim(min_value - pad, max_value + pad)
    for axis in flat_axes[len(areas) :]:
        axis.set_visible(False)


def _model_names(df) -> list[str]:
    if df is None or df.empty or "model_name" not in df.columns:
        return []
    names = [str(name) for name in df["model_name"].dropna().unique()]
    preferred_order = {"LinearRegression": 0, "SeasonalNaive": 1, "RidgeRegression": 2}
    return sorted(names, key=lambda name: (preferred_order.get(name, 99), name))


def _model_color_map(model_names: list[str]) -> dict[str, str]:
    preferred = {
        "LinearRegression": "#3158d4",
        "SeasonalNaive": "#1a7f37",
        "RidgeRegression": "#bf3989",
    }
    fallback = ["#8250df", "#d1242f", "#9a6700", "#0550ae", "#57606a"]
    colors = {}
    fallback_idx = 0
    for name in model_names:
        if name in preferred:
            colors[name] = preferred[name]
        else:
            colors[name] = fallback[fallback_idx % len(fallback)]
            fallback_idx += 1
    return colors


def _actual_vs_predicted_size(df) -> tuple[float, float]:
    import math

    areas = [] if df is None or df.empty else sorted(df["area"].dropna().unique())
    cols = min(3, max(1, len(areas)))
    rows = max(1, math.ceil(max(len(areas), 1) / cols))
    return 4.4 * cols, 3.4 * rows
