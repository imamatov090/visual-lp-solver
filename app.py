import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- CSS стили ---
st.markdown("""
<style>
/* Радиокнопки как сегментированный контрол */
.css-1cpxl2u {
    flex-direction: row !important;
}
.css-1cpxl2u label {
    min-width: 65px !important;
    height: 38px !important;
    border-radius: 10px !important;
    border: 1.5px solid #007bff !important;
    background-color: #f8f9fa !important;
    color: #007bff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: 500 !important;
    transition: all 0.2s ease-in-out;
    margin: 0 4px !important;
    white-space: nowrap !important;
}
.css-1cpxl2u input:checked + label {
    background-color: #007bff !important;
    color: white !important;
    box-shadow: 0 0 6px rgba(0,123,255,0.4);
}

/* Кнопки */
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

/* Карточка результата */
.result-card {
    background: linear-gradient(90deg, rgba(0,123,255,0.15) 0%, rgba(0,212,255,0.15) 100%);
    border-left: 5px solid #007bff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-top: 0.8rem;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")
    col1, col2, col3, col4, col5 = st.columns([1, 0.2, 1, 0.2, 1.2])
    with col1:
        a1 = st.number_input("Коэф. при x", value=5.3, key="a1", label_visibility="collapsed")
    with col2:
        st.write("x +")
    with col3:
        a2 = st.number_input("Коэф. при y", value=-7.1, key="a2", label_visibility="collapsed")
    with col4:
        st.write("y →")
    with col5:
        opt_type = st.radio("", ["max", "min"], index=0, horizontal=True, key="opt_type")

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
        st.experimental_rerun()

    for i, cons in enumerate(st.session_state.constraints):
        cols = st.columns([1, 0.2, 1, 0.3, 1, 0.9, 0.3])
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}", label_visibility="collapsed")
        with cols[1]:
            st.write("x +")
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}", label_visibility="collapsed")
        with cols[3]:
            st.write("y")
        with cols[4]:
            cons["sign"] = st.radio(
                "", ["≤", "≥", "="], index=["≤", "≥", "="].index(cons["sign"]),
                horizontal=True, key=f"sign{i}"
            )
        with cols[5]:
            cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}", label_visibility="collapsed")
        with cols[6]:
            if st.button("🗑", key=f"del{i}"):
                remove_constraint(i)

    col_add, col_solve, col_clear = st.columns(3)
    with col_add:
        st.button("+ Добавить", on_click=add_constraint)
    with col_solve:
        solve = st.button("Решить")
    with col_clear:
        if st.button("Очистить"):
            st.session_state.constraints = []
            st.session_state.results = []
            st.experimental_rerun()

# --- Заголовок ---
st.title("📊 Линейное программирование — Графический решатель")

# --- Решение ---
if solve:
    X = np.linspace(-20, 20, 600)
    lines = []
    for cons in st.session_state.constraints:
        c, d, b, sign = cons["c"], cons["d"], cons["b"], cons["sign"]
        if abs(d) < 1e-8:
            st.warning(f"Ограничение {i+1}: коэффициент при y не может быть нулевым!")
            continue
        lines.append((c, d, b, sign))

    if len(lines) < 2:
        st.error("Нужно минимум 2 ограничения с ненулевым коэффициентом при y.")
    else:
        # --- Пересечения ---
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

        # --- Проверка допустимости ---
        feas = []
        for (x, y) in pts:
            ok = True
            for (c, d, b, sign) in lines:
                val = c * x + d * y
                if (sign == "≤" and val > b + 1e-6) or \
                   (sign == "≥" and val < b - 1e-6) or \
                   (sign == "=" and abs(val - b) > 1e-6):
                    ok = False
                    break
            if ok:
                feas.append((x, y))

        # --- Оптимум ---
        if feas:
            z_values = [a1 * x + a2 * y for x, y in feas]
            if opt_type == "max":
                best_idx = np.argmax(z_values)
                color_max, color_min = "red", "blue"
            else:
                best_idx = np.argmin(z_values)
                color_max, color_min = "blue", "red"

            ox, oy = feas[best_idx]
            zopt = z_values[best_idx]

            # Сохраняем только последние 5
            new_result = {
                "№": len(st.session_state.results) + 1,
                "x": round(ox, 3),
                "y": round(oy, 3),
                "z": round(zopt, 3),
                "type": opt_type
            }
            st.session_state.results.append(new_result)
            st.session_state.results = st.session_state.results[-5:]

        else:
            ox = oy = zopt = None
            st.warning("Область допустимых решений пуста или не ограничена.")

        # --- График ---
        fig = go.Figure()
        colors = ["#007bff", "#ff9800", "#9c27b0", "#4caf50", "#f44336", "#795548"]

        for i, (c, d, b, sign) in enumerate(lines):
            with st.sidebar():
    st.markdown("### 🎯 Целевая функция")

    col1, col2, col3, col4, col5 = st.columns([1, 0.2, 1, 0.2, 1.2])
    with col1:
        a1 = st.number_input("", value=5.3, key="a1")
    with col2:
        st.write("*x +")
    with col3:
        a2 = st.number_input("", value=-7.1, key="a2")
    with col4:
        st.write("*y →")
    with col5:
        opt_type = st.radio(
            "", ["max", "min"],
            index=0,
            horizontal=True,
            key="opt_type"
        )

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

    for i, cons in enumerate(st.session_state.constraints):
        cols = st.columns([1, 0.2, 1, 0.3, 1, 0.9, 0.3])
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
        (a1_, b1_, c1_, _), (a2_, b2_, c2_, _) = l1, l2
        det = a1_ * b2_ - a2_ * b1_
        if abs(det) < 1e-8:
            return None
        x = (c1_ * b2_ - c2_ * b1_) / det
        y = (a1_ * c2_ - a2_ * c1_) / det
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
            if (sign == "≤" and val > b) or (sign == "≥" and val < b) or (sign == "=" and abs(val - b) > 1e-6):
                ok = False
                break
        if ok:
            feas.append((x, y))

    if feas:
        z = [a1 * x + a2 * y for (x, y) in feas]
        best = np.argmax(z) if opt_type == "max" else np.argmin(z)
        ox, oy, zopt = *feas[best], z[best]

        # 🔹 faqat oxirgi 5 ta natijani saqlash
        st.session_state.results = st.session_state.results[-4:]

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
        Y = (b - c * X) / d
        fig.add_trace(go.Scatter(
            x=X, y=Y, mode="lines",
            line=dict(color=colors[i % len(colors)].replace("0.3", "1.0"), width=2),
            fill="tonexty" if sign in ["≤", "≥"] else None,
            fillcolor=colors[i % len(colors)],
            name=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}"
        ))

    # 🔹 Целевая прямая — ikki rangli (qizil / ko‘k)
    if feas:
        z_line = zopt
        x_split = ox
        y_split = (z_line - a1 * x_split) / a2 if abs(a2) > 1e-8 else None

        if y_split is not None:
            X_left = X[X <= x_split]
            X_right = X[X >= x_split]
            Y_left = (z_line - a1 * X_left) / a2
            Y_right = (z_line - a1 * X_right) / a2

            # 🔵 min tomoni
            fig.add_trace(go.Scatter(
                x=X_left, y=Y_left, mode="lines",
                line=dict(color="blue", width=3, dash="dot"),
                name="Минимум (голубой)"
            ))

            # 🔴 max tomoni
            fig.add_trace(go.Scatter(
                x=X_right, y=Y_right, mode="lines",
                line=dict(color="red", width=3, dash="dot"),
                name="Максимум (красный)"
            ))

        # ⭐ Optimum nuqta
        fig.add_trace(go.Scatter(
            x=[ox], y=[oy],
            mode="markers+text",
            text=[f"({ox:.2f},{oy:.2f})"],
            textposition="top center",
            marker=dict(color="gold", size=12, line=dict(color="black", width=1)),
            name="⭐ Оптимум"
        ))

    # 🔳 Setka — kichikroq oraliqda
    fig.update_layout(
        title="График решения",
        xaxis_title="x",
        yaxis_title="y",
        height=500,
        template="plotly_white",
        xaxis=dict(showgrid=True, gridwidth=0.6, gridcolor="LightGray", dtick=2),
        yaxis=dict(showgrid=True, gridwidth=0.6, gridcolor="LightGray", dtick=2),
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)", bordercolor="gray", borderwidth=1)
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Natijalar --- #
if st.session_state.results:
    st.markdown("### 🧮 История решений (последние 5)")

    for res in reversed(st.session_state.results):
        if res["type"] == "max":
            bg_color = "rgba(255, 0, 0, 0.1)"
            border_color = "red"
            type_text = "МАКСИМУМ"
        else:
            bg_color = "rgba(0, 123, 255, 0.1)"
            border_color = "blue"
            type_text = "МИНИМУМ"

        st.markdown(
            f"<div style='background:{bg_color}; border-left:5px solid {border_color}; "
            f"border-radius:10px; padding:0.8rem 1rem; margin-top:0.8rem; font-size:15px;'>"
            f"<b>f<sub>{res['№']}</sub>(x, y)</b> = <span style='font-size:1.1em; color:#d32f2f;'>{res['z']}</span> &nbsp;&nbsp; "
            f"<i>при</i> (x = {res['x']}, y = {res['y']}) &nbsp;&nbsp; "
            f"<b>Тип:</b> {type_text}"
            f"</div>",
            unsafe_allow_html=True
        )
