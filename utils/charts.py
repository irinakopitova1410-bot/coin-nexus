import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

COLORS = {"safe": "#4ADE80", "grey": "#FCD34D", "distress": "#F87171"}

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
        title={"text": title, "font": {"color": "#F1F5F9", "size": 16}},
        number={"font": {"color": color, "size": 40}, "suffix": ""},
        gauge={
            "axis": {"range": [min_val, max_val], "tickcolor": "#64748B",
                     "tickfont": {"color": "#94A3B8"}},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#1E293B",
            "borderwidth": 0,
            "steps": [
                {"range": [min_val, grey_low], "color": "#450A0A"},
                {"range": [grey_low, safe], "color": "#422006"},
                {"range": [safe, max_val], "color": "#14532D"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": value
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
        font={"color": "#F1F5F9"}, height=300,
        margin=dict(t=60, b=20, l=30, r=30)
    )
    return fig

def radar_chart(categories: List[str], values: List[float], title: str) -> go.Figure:
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(59,130,246,0.2)",
        line=dict(color="#3B82F6", width=2),
        marker=dict(color="#3B82F6", size=8)
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont={"color": "#94A3B8"},
                            gridcolor="#334155", linecolor="#334155"),
            angularaxis=dict(tickfont={"color": "#CBD5E1"}, gridcolor="#334155",
                             linecolor="#334155"),
            bgcolor="#1E293B"
        ),
        paper_bgcolor="#0F172A", plot_bgcolor="#0F172A",
        font={"color": "#F1F5F9"}, title={"text": title, "font": {"color": "#F1F5F9"}},
        height=350, margin=dict(t=60, b=20, l=30, r=30), showlegend=False
    )
    return fig

def bar_chart(labels: List[str], values: List[float], title: str) -> go.Figure:
    colors_list = ["#4ADE80" if v >= 70 else "#FCD34D" if v >= 45 else "#F87171" for v in values]
    fig = go.Figure(go.Bar(
        x=labels, y=values, marker_color=colors_list,
        text=[f"{v:.1f}" for v in values], textposition="auto",
        textfont={"color": "#F1F5F9", "size": 12}
    ))
    fig.update_layout(
        paper_bgcolor="#0F172A", plot_bgcolor="#1E293B",
        font={"color": "#F1F5F9"}, title={"text": title, "font": {"color": "#F1F5F9"}},
        xaxis=dict(tickfont={"color": "#94A3B8"}, gridcolor="#334155"),
        yaxis=dict(range=[0,100], tickfont={"color": "#94A3B8"}, gridcolor="#334155"),
        height=300, margin=dict(t=60, b=20, l=30, r=30)
    )
    return fig

def projection_chart(projections: List[Dict]) -> go.Figure:
    anni = [p["Anno"] for p in projections]
    base = [p["Scenario Base"] for p in projections]
    stress = [p["Scenario Stress"] for p in projections]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=anni, y=base, mode="lines+markers",
                              name="Scenario Base (+15%)", line=dict(color="#4ADE80", width=2),
                              marker=dict(size=8)))
    fig.add_trace(go.Scatter(x=anni, y=stress, mode="lines+markers",
                              name="Scenario Stress (-10%)", line=dict(color="#F87171", width=2, dash="dot"),
                              marker=dict(size=8)))
    fig.update_layout(
        paper_bgcolor="#0F172A", plot_bgcolor="#1E293B",
        font={"color": "#F1F5F9"}, title={"text": "Proiezioni Z-Score (4 anni)", "font": {"color": "#F1F5F9"}},
        legend=dict(bgcolor="#1E293B", bordercolor="#334155"),
        xaxis=dict(tickfont={"color": "#94A3B8"}, gridcolor="#334155"),
        yaxis=dict(tickfont={"color": "#94A3B8"}, gridcolor="#334155"),
        height=300, margin=dict(t=60, b=20, l=30, r=30)
    )
    return fig
