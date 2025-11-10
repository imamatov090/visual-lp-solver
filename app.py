import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# 💙 CSS — eski shakl (dumaloq) ammo ko‘k rangda
st.markdown("""
<style>
/* Radiolar (≤ ≥ =) ko‘k rangda, dumaloq */
div[role="radiogroup"] label div:first-child {
    border: 2px solid #007bff !important;
    border-radius: 50% !important;
}
div[role="radiogroup"] input:checked + div:first-child {
    background-color: #007bff !important;
    border-color: #007bff !important;
}

/* Tugmalar ko‘k */
.stButton > button {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 0.5rem 1rem !important;
}
.stButton > button:hover {
    background-color: #0056b3 !important;
}

/* “Удалить” tugmasi */
button[kind="secondary"] {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 6px !important;
}
button[kind="secondary"]:hover {
    background-color: #0056b3 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar --- #
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")

    # 🔹 bir qatorda: 5.3 * x + -7.1 * y → max
    col1, col2, col3, col4, col5, col6 = st.columns([1, 0.2, 1, 0.2, 0.5, 0.8])
    with col1:
        a1 = st.number_input("", value=5.3, key="a1")
    with col2:
        st.write("*x +")
    with col3:
        a2 = st.number_input("", value=-7.1, key="a2")
    with col4:
        st.write("*y →")
    with col5:
        opt_type = st.radio("", ["max", "min"], horizontal=True, key="opt_type")

    st.markdown("### ✏️ Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "≤", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
        ]
    if "results" not in st.session_state:
        st.session_state.results = []

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})
    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    # 🔹 Cheklovlar
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
        st.session_state.results = []
        st.experimental_rerun()

st.title("📊 Линейное программирование — Решатель")

# --- Hisoblash qismi --- #
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
        det = a1*b2 - a2*b1
        if abs(det) < 1e-8:
            return None
        x = (c1*b2 - c2*b1)/det
        y = (a1*c2 - a2*c1)/det
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
            val = c*x + d*y
            if (sign == "≤" and val > b) or (sign == "≥" and val < b) or (sign == "=" and abs(val - b) > 1e-6):
                ok = False; break
        if ok:
            feas.append((x, y))

    if feas:
        z = [a1*x + a2*y for (x, y) in feas]
        best = np.argmax(z) if opt_type == "max" else np.argmin(z)
        ox, oy, zopt = *feas[best], z[best]
        result_id = len(st.session_state.results) + 1
        st.session_state.results.append({
            "№": result_id,
            "x": round(ox, 3),
            "y": round(oy, 3),
            "z": round(zopt, 3),
            "type": opt_type
        })
    else:
        ox = oy = zopt = None

    fig = go.Figure()
    colors = ["rgba(0,123,255,0.3)", "rgba(255,152,0,0.3)", "rgba(156,39,176,0.3)",
              "rgba(76,175,80,0.3)", "rgba(244,67,54,0.3)", "rgba(121,85,72,0.3)"]

    for i, (c, d, b, sign) in enumerate(lines):
        Y = (b - c*X) / d
        fig.add_trace(go.Scatter(
            x=X, y=Y, mode="lines",
            line=dict(color=colors[i % len(colors)].replace("0.3", "1.0"), width=2),
            fill="tonexty" if sign in ["≤", "≥"] else None,
            fillcolor=colors[i % len(colors)],
            name=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}"
        ))

    if feas:
        fig.add_trace(go.Scatter(
            x=[ox], y=[oy], mode="markers+text",
            text=[f"({ox:.2f},{oy:.2f})"], textposition="top center",
            marker=dict(color="gold", size=12, line=dict(color="black", width=1)),
            name="⭐ Оптимум"
        ))

    fig.update_layout(title="График решения", xaxis_title="x", yaxis_title="y",
                      height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- Natijalar --- #
if st.session_state.results:
    st.markdown("### 🧮 История решений (значения функции)")
    results = st.session_state.results
    for i, res in enumerate(reversed(results)):
        st.latex(fr"f_{{{res['№']}}}(x, y) = {res['z']} \\quad \\text{{при}} \\quad x={res['x']}, \\; y={res['y']}")
