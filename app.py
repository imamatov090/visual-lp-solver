import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- Sidebar (chap panel) ---
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")
    a1 = st.number_input("Коэффициент при x₁", value=2500.0, key="a1")
    a2 = st.number_input("Коэффициент при x₂", value=3500.0, key="a2")
    opt_type = st.radio("Тип оптимизации:", ["max", "min"], horizontal=True)

    st.markdown("### ✏️ Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 6, "d": 6, "sign": "≤", "b": 240},
            {"c": 16, "d": 4, "sign": "≤", "b": 400},
            {"c": 3, "d": 10, "sign": "≤", "b": 330},
        ]
    if "results" not in st.session_state:
        st.session_state.results = []

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})
    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    for i, cons in enumerate(st.session_state.constraints):
        cols = st.columns([1, 0.2, 1, 0.3, 1, 0.8, 0.3])
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}")
        with cols[1]:
            st.write("x₁ +")
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}")
        with cols[3]:
            st.write("x₂")
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

# --- Asosiy qism ---
st.title("📊 Линейное программирование — Решатель")

if solve:
    X = np.linspace(-10, 60, 400)
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
        if p and -10 < p[0] < 60 and -10 < p[1] < 60:
            pts.append(p)

    feas = []
    for (x, y) in pts:
        ok = True
        for (c, d, b, sign) in lines:
            val = c*x + d*y
            if (sign == "≤" and val > b) or (sign == "≥" and val < b) or (sign == "=" and abs(val - b) > 1e-6):
                ok=False; break
        if ok:
            feas.append((x, y))

    if feas:
        z = [a1*x + a2*y for (x, y) in feas]
        best = np.argmax(z) if opt_type=="max" else np.argmin(z)
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

    # --- Grafik ---
    fig = go.Figure()
    colors = ["green", "red", "blue", "orange", "purple"]

    for i,(c,d,b,sign) in enumerate(lines):
        Y = (b - c*X) / d
        fig.add_trace(go.Scatter(
            x=X, y=Y, mode="lines",
            line=dict(color=colors[i%len(colors)], width=2),
            name=f"{c}x₁ + {d}x₂ {sign} {b}"
        ))
        fig.add_annotation(
            x=X[-1], y=Y[-1],
            text=f"{c}x₁ + {d}x₂ = {b}",
            showarrow=False, font=dict(color=colors[i%len(colors)], size=13)
        )

    # Feasible soha (agar topilgan bo‘lsa)
    if feas:
        feas_poly = np.array(feas)
        hull = feas_poly[np.argsort(
            np.arctan2(
                feas_poly[:,1] - np.mean(feas_poly[:,1]),
                feas_poly[:,0] - np.mean(feas_poly[:,0])
            )
        )]   # ✅ Qavslar to‘g‘rilangan
        fig.add_trace(go.Scatter(
            x=hull[:,0], y=hull[:,1],
            fill="toself", fillcolor="rgba(0,150,255,0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Feasible region"
        ))

    # Maqsad funksiyasi (qora qalin chiziq)
    if ox is not None:
        target = a1*ox + a2*oy
        Yt = (target - a1*X) / a2
        fig.add_trace(go.Scatter(
            x=X, y=Yt, mode="lines",
            line=dict(color="black", width=3, dash="dash"),
            name=f"{a1}x₁ + {a2}x₂ = {round(target,2)}"
        ))

    # Optimal nuqta
    if ox is not None:
        fig.add_trace(go.Scatter(
            x=[ox], y=[oy],
            mode="markers+text",
            text=[f"({ox:.2f}, {oy:.2f})"],
            textposition="top center",
            marker=dict(size=12, color="red"),
            name="⭐ Оптимум"
        ))

    fig.update_layout(
        title="График решения",
        xaxis_title="x₁",
        yaxis_title="x₂",
        xaxis=dict(range=[-5, 50]),
        yaxis=dict(range=[-5, 50]),
        template="plotly_white",
        height=600,
        legend=dict(x=0.75, y=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Tarix (LaTeX formula bilan) ---
if st.session_state.results:
    st.markdown("### 🧮 История решений (значения функции)")

    results = st.session_state.results
    for i, res in enumerate(reversed(results)):
        st.latex(fr"f_{{{res['№']}}}(x₁, x₂) = {res['z']} \quad \text{{при}} \quad x₁={res['x']}, \; x₂={res['y']}")

    if len(results) >= 2:
        last = results[-1]
        prev = results[-2]
        if last["z"] > prev["z"]:
            st.success("📈 Новое решение лучше:")
            st.latex(fr"f_{{{last['№']}}}({last['x']},{last['y']}) = {last['z']} \; > \; f_{{{prev['№']}}}({prev['x']},{prev['y']}) = {prev['z']}")
        elif last["z"] < prev["z"]:
            st.error("📉 Новое решение хуже:")
            st.latex(fr"f_{{{last['№']}}}({last['x']},{last['y']}) = {last['z']} \; < \; f_{{{prev['№']}}}({prev['x']},{prev['y']}) = {prev['z']}")
        else:
            st.info("⚖️ Значения равны:")
            st.latex(fr"f_{{{last['№']}}} = f_{{{prev['№']}}} = {last['z']}")
