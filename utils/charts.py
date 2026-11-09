import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

# Palette Aurora (tema chiaro)
INK = "#0B1230"
MUTED = "#5A6478"
ACCENT = "#1E376C"
BORDER = "#E2E8F0"
PLOT_BG = "#F4F7FD"
COLORS = {"safe": "#16A34A", "grey": "#D97706", "distress": "#DC2626"}


def _base_layout(fig: go.Figure, height: int = 300, title: str = ""):
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor=PLOT_BG,
        font={"color": INK, "family": "Inter, sans-serif"},
        title={"text": title, "font": {"color": INK, "size": 15}} if title else None,
        xaxis=dict(tickfont={"color": MUTED}, gridcolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(tickfont={"color": MUTED}, gridcolor=BORDER, zerolinecolor=BORDER),
        height=height, margin=dict(t=60, b=20, l=30, r=30),
    )


def gauge_chart(value: float, title: str, min_val: float, max_val: float,
                thresholds: Dict[str, float]) -> go.Figure:
    safe = thresholds.get("safe", 2.99)
    grey_low = thresholds.get("grey_low", 1.81)

    if value > safe: color = COLORS["safe"]
    elif value >= grey_low: color = COLORS["grey"]
    else: color = COLORS["distress"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={"text": title, "font": {"color": INK, "size": 15}},
        number={"font": {"color": color, "size": 40}, "suffix": ""},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": MUTED,
                     "tickfont": {"color": MUTED}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#EEF2FA",
            "borderwidth": 0,
            "steps": [
                {"range": [min_val, grey_low], "color": "#FEE2E2"},
                {"range": [grey_low, safe], "color": "#FEF3C7"},
                {"range": [safe, max_val], "color": "#DCFCE7"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": value
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", font={"color": INK, "family": "Inter, sans-serif"},
        height=300, margin=dict(t=60, b=20, l=30, r=30)
    )
    return fig


def radar_chart(categories: List[str], values: List[float], title: str) -> go.Figure:
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(30,55,108,0.15)",
        line=dict(color=ACCENT, width=2.5),
        marker=dict(color=ACCENT, size=7)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont={"color": MUTED},
                            gridcolor=BORDER, linecolor=BORDER),
            angularaxis=dict(tickfont={"color": INK}, gridcolor=BORDER,
                             linecolor=BORDER),
            bgcolor="#FFFFFF"
        ),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#FFFFFF",
        font={"color": INK, "family": "Inter, sans-serif"},
        title={"text": title, "font": {"color": INK, "size": 15}},
        height=350, margin=dict(t=60, b=20, l=30, r=30), showlegend=False
    )
    return fig


def bar_chart(labels: List[str], values: List[float], title: str) -> go.Figure:
    colors_list = ["#16A34A" if v >= 70 else "#D97706" if v >= 45 else "#DC2626" for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors_list,
        text=[f"{v:.1f}" for v in values], textposition="auto",
        textfont={"color": INK, "size": 12}
    ))
    _base_layout(fig, 300, title)
    fig.update_layout(yaxis=dict(range=[0, 100], tickfont={"color": MUTED}, gridcolor=BORDER))
    return fig


def projection_chart(projections: List[Dict]) -> go.Figure:
    anni = [p["Anno"] for p in projections]
    base = [p["Scenario Base"] for p in projections]
    stress = [p["Scenario Stress"] for p in projections]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anni, y=base, mode="lines+markers",
                              name="Scenario Base (+15%)", line=dict(color="#16A34A", width=3),
                              marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=anni, y=stress, mode="lines+markers",
                              name="Scenario Stress (-10%)", line=dict(color="#DC2626", width=3, dash="dot"),
                              marker=dict(size=8)))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor=PLOT_BG,
        font={"color": INK, "family": "Inter, sans-serif"},
        title={"text": "Proiezioni Z-Score (4 anni)", "font": {"color": INK, "size": 15}},
        legend=dict(bgcolor="#FFFFFF", bordercolor=BORDER, font={"color": INK}),
        xaxis=dict(tickfont={"color": MUTED}, gridcolor=BORDER),
        yaxis=dict(tickfont={"color": MUTED}, gridcolor=BORDER),
        height=300, margin=dict(t=60, b=20, l=30, r=30)
    )
    return fig
