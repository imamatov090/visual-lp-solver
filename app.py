import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

# --- Sahifa sozlamalari ---
st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- Chap panel ---
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")
    a1 = st.number_input("Коэффициент при x", value=5.3, key="a1")
    a2 = st.number_input("Коэффициент при y", value=-7.1, key="a2")
    opt_type = st.radio("Тип оптимизации:", ["max", "min"], horizontal=True)

    st.markdown("### ✏️ Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "≤", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
            {"c": 3.2, "d": -6.0, "sign": "≥", "b": 7.0},
            {"c": 7.0, "d": -2.0, "sign": "≤", "b": 10.0},
            {"c": -6.5, "d": 3.0, "sign": "≤", "b": 9.0},
        ]

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})

    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    for i, cons in enumerate(st.session_state.constraints):
        cols = st.columns([1, 0.2, 1, 0.3, 1, 0.8, 0.3])
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}")
        with cols[1]:
            st.write("x +")
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}")
        with cols[3]:
            st.write("y")
        with cols[4]:
            cons["sign"] = st.radio(
                "",
                ["≤", "≥", "="],
                index=["≤", "≥", "="].index(cons["sign"]),
                horizontal=True,
                key=f"sign{i}"
            )
        with cols[5]:
            cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}")
        with cols[6]:
            if st.button("🗑", key=f"del{i}"):
                remove_constraint(i)
                st.experimental_rerun()

    st.button("+ Добавить", on_click=add_constraint)
    solve = st.button("Решить")
    if st.button("Очистить"):
        st.session_state.constraints = []
        st.experimental_rerun()

# --- Asosiy qism ---
st.title("📊 Линейное программирование — Решатель")

if solve:
    X = np.linspace(-20, 20, 600)
    lines = []
    for cons in st.session_state.constraints:
        c, d, b, sign = cons["c"], cons["d"], cons["b"], cons["sign"]
        if abs(d) < 1e-8:
            continue
        lines.append((c, d, b, sign))

    def intersect(l1, l2):
        (a1, b1, c1, _), (a2, b2, c2, _) = l1, l2
        det = a1 * b2 - a2 * b1
        if abs(det) < 1e-8:
            return None
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        return (x, y)

    pts = []
    for l1, l2 in combinations(lines, 2):
        p = intersect(l1, l2)
        if p and -50 < p[0] < 50 and -50 < p[1] < 50:
            pts.append(p)

    feas = []
    for (x, y) in pts:
        ok = True
        for (c, d, b, sign) in lines:
            val = c * x + d * y
            if (sign == "≤" and val > b) or (sign == "≥" and val < b) or (
                sign == "=" and abs(val - b) > 1e-6
            ):
                ok = False
                break
        if ok:
            feas.append((x, y))

    if feas:
        z = [a1 * x + a2 * y for (x, y) in feas]
        best = np.argmax(z) if opt_type == "max" else np.argmin(z)
        ox, oy, zopt = *feas[best], z[best]
    else:
        ox = oy = zopt = None

    # --- Rangli interaktiv grafik ---
    fig = go.Figure()
    colors = [
        "rgba(0,123,255,0.3)",
        "rgba(255,152,0,0.3)",
        "rgba(156,39,176,0.3)",
        "rgba(76,175,80,0.3)",
        "rgba(244,67,54,0.3)",
        "rgba(121,85,72,0.3)",
        "rgba(0,188,212,0.3)",
    ]

    for i, (c, d, b, sign) in enumerate(lines):
        Y = (b - c * X) / d
        fill_to = "tonexty" if sign == "≤" else "none"
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                line=dict(color=colors[i % len(colors)].replace("0.3", "1.0"), width=2),
                fill="tonexty" if sign in ["≤", "≥"] else None,
                fillcolor=colors[i % len(colors)],
                name=f"{c:.2f} * x + {d:.2f} * y {sign} {b:.2f}",
                hoverinfo="x+y+name",
            )
        )

    if feas:
        fx, fy = zip(*feas)
        fig.add_trace(
            go.Scatter(
                x=fx,
                y=fy,
                mode="markers",
                marker=dict(color="red", size=8),
                name="Угловые точки",
                hovertemplate="x=%{x:.2f}<br>y=%{y:.2f}",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=[ox],
                y=[oy],
                mode="markers+text",
                marker=dict(
                    color="gold", size=12, line=dict(color="black", width=1)
                ),
                name="⭐ Оптимум",
                text=[f"({ox:.2f}, {oy:.2f})"],
                textposition="top center",
            )
        )
        if abs(a2) > 1e-8:
            Yz = (zopt - a1 * X) / a2
            fig.add_trace(
                go.Scatter(
                    x=X,
                    y=Yz,
                    mode="lines",
                    line=dict(color="black", width=1, dash="dash"),
                    name=f"Целевая прямая: {a1:.2f} * x + {a2:.2f} * y = {zopt:.2f}",
                )
            )

    fig.update_layout(
        title="График решения (с цветными областями)",
        xaxis_title="x",
        yaxis_title="y",
        legend=dict(bgcolor="rgba(255,255,255,0.7)", bordercolor="gray", borderwidth=1),
        height=550,
        template="plotly_white",
    )

    st.plotly_chart(fig, use_container_width=True)
