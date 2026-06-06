from __future__ import annotations


def actual_vs_predicted_figure(df):
    from matplotlib.figure import Figure

    fig = Figure(figsize=_actual_vs_predicted_size(df), tight_layout=True)
    draw_actual_vs_predicted(fig, df)
    return fig


def draw_actual_vs_predicted(figure, df) -> None:
    import math

    areas = [] if df is None or df.empty else sorted(df["area"].dropna().unique())
    model_names = _model_names(df) or ["LinearRegression"]
    model_colors = _model_color_map(model_names)
    cols = min(3, max(1, len(areas)))
    area_rows = max(1, math.ceil(max(len(areas), 1) / cols))
    rows = area_rows * max(1, len(model_names))
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

    for model_idx, model_name in enumerate(model_names):
        model_df = _model_dataframe(df, model_name)
        for area_idx, area in enumerate(areas):
            axis = axes[model_idx * area_rows + area_idx // cols][area_idx % cols]
            group = model_df[model_df["area"].eq(area)]
            if group.empty:
                axis.set_visible(False)
                continue
            _draw_actual_vs_predicted_axis(
                axis,
                group,
                area=area,
                model_name=model_name,
                color=model_colors.get(model_name, "#3158d4"),
            )
        for area_idx in range(len(areas), area_rows * cols):
            axis = axes[model_idx * area_rows + area_idx // cols][area_idx % cols]
            axis.set_visible(False)


def _draw_actual_vs_predicted_axis(axis, group, area: str, model_name: str, color: str):
    actual = group["actual_kwh"].astype(float)
    predicted = group["predicted_kwh"].astype(float)
    min_value = min(float(actual.min()), float(predicted.min()))
    max_value = max(float(actual.max()), float(predicted.max()))
    pad = max((max_value - min_value) * 0.08, 1.0)
    axis.scatter(actual, predicted, s=14, color=color, alpha=0.65)
    axis.plot(
        [min_value - pad, max_value + pad],
        [min_value - pad, max_value + pad],
        linestyle="--",
        color="#d55e5e",
        linewidth=1.3,
    )
    axis.set_title(f"{_model_label(model_name)} - {area}")
    axis.set_xlabel("Actual kWh")
    axis.set_ylabel("Predicted kWh")
    axis.grid(True, alpha=0.2)
    axis.set_xlim(min_value - pad, max_value + pad)
    axis.set_ylim(min_value - pad, max_value + pad)


def _model_dataframe(df, model_name: str):
    if df is None or df.empty or "model_name" not in df.columns:
        return df
    return df[df["model_name"].astype(str).eq(model_name)]


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


def _model_label(model_name: str) -> str:
    return {
        "LinearRegression": "Linear",
        "RidgeRegression": "Ridge",
    }.get(model_name, model_name)


def _actual_vs_predicted_size(df) -> tuple[float, float]:
    import math

    areas = [] if df is None or df.empty else sorted(df["area"].dropna().unique())
    model_count = max(1, len(_model_names(df)))
    cols = min(3, max(1, len(areas)))
    area_rows = max(1, math.ceil(max(len(areas), 1) / cols))
    return 4.4 * cols, 3.2 * area_rows * model_count
