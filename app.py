import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# Streamlit sahifa sozlamalari
st.set_page_config(page_title="📊 Линейное программирование — Решатель", layout="wide")

# --- CSS chiroyli ko'rinish uchun ---
st.markdown("""
    <style>
        body { background-color: #f8f9fa; }
        .stApp { background-color: #f8f9fa; }
        div[data-testid="stVerticalBlock"] { gap: 1rem; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        h1, h3 { color: #2c3e50; }
        .stButton button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #0056b3;
            color: #fff;
        }
        .stTextInput>div>div>input, .stNumberInput>div>div>input {
            border-radius: 8px;
        }
        .graph-box {
            background-color: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# --- Sarlavha ---
st.markdown("<h1 style='text-align:center;'>📈 Линейное программирование — Решатель</h1>", unsafe_allow_html=True)
st.caption("Интерактивная визуализация задачи линейного программирования (2 переменные)")

# --- Chap va o‘ng ustunlar ---
col_left, col_right = st.columns([1, 2])  # chap: 1 qism, o‘ng: 2 qism

# ===== CHAP PANEL =====
with col_left:
    st.markdown("### 🎯 Целевая функция")
    col1, col2, col3, col4 = st.columns([1, 0.3, 1, 0.7])
    with col1:
        a1 = st.number_input("", value=5.3, key="a1")
    with col2:
        st.markdown("*x +*")
    with col3:
        a2 = st.number_input("", value=-7.1, key="a2")
    with col4:
        opt_type = st.selectbox("", ["max", "min"], key="opt")

    st.markdown("### 📏 Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "=", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
            {"c": 3.2, "d": -6.0, "sign": "≥", "b": 7.0},
            {"c": 7.0, "d": -2.0, "sign": "≤", "b": 10.0},
            {"c": -6.5, "d": 3.0, "sign": "≤", "b": 9.0}
        ]

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})

    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    for i, cons in enumerate(st.session_state.constraints):
        cols = st.columns([1, 0.2, 1, 0.2, 0.6, 0.6, 0.2])
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}")
        with cols[1]:
            st.markdown("*x +*")
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}")
        with cols[3]:
            st.markdown("*y*")
        with cols[4]:
            cons["sign"] = st.selectbox("", ["≤", "≥", "="], index=["≤", "≥", "="].index(cons["sign"]), key=f"sign{i}")
        with cols[5]:
            cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}")
        with cols[6]:
            st.button("🟥", key=f"del{i}", on_click=remove_constraint, args=(i,))

    st.button("+ Добавить ограничение", on_click=add_constraint)
    st.markdown("<p style='font-size: 13px; color: gray;'>Коэффициенты можно вводить целыми или дробными (запятая/точка).</p>", unsafe_allow_html=True)

    colA, colB, colC = st.columns([1, 1, 1])
    solve = colA.button("Решить")
    clear = colB.button("Очистить")
    export_pdf = colC.button("Скачать отчёт (PDF)")

    if clear:
        st.session_state.constraints = []
        st.experimental_rerun()

# ===== O‘NG PANEL (grafik) =====
with col_right:
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

        points = []
        for l1, l2 in combinations(lines, 2):
            p = intersect(l1, l2)
            if p and -50 < p[0] < 50 and -50 < p[1] < 50:
                points.append(p)

        feasible = []
        for (x, y) in points:
            ok = True
            for (c, d, b, sign) in lines:
                val = c * x + d * y
                if (sign == "≤" and val > b + 1e-6) or (sign == "≥" and val < b - 1e-6) or (sign == "=" and abs(val - b) > 1e-6):
                    ok = False
                    break
            if ok:
                feasible.append((x, y))

        if feasible:
            z_values = [a1 * x + a2 * y for (x, y) in feasible]
            best_idx = np.argmax(z_values) if opt_type == "max" else np.argmin(z_values)
            opt_x, opt_y = feasible[best_idx]
            z_opt = z_values[best_idx]
        else:
            opt_x, opt_y, z_opt = None, None, None

        with st.container():
            st.markdown("<div class='graph-box'>", unsafe_allow_html=True)
            st.markdown("### 📉 График решения")

            fig, ax = plt.subplots(figsize=(9, 7))
            colors = ['#007bff', '#ff9800', '#9c27b0', '#4caf50', '#f44336', '#795548', '#00bcd4']

            # Chiziqlarni chizish va sohalarni to‘ldirish
            for idx, (c, d, b, sign) in enumerate(lines):
                Y = (b - c * X) / d
                ax.plot(X, Y, label=f"{c:.2f} * x + {d:.2f} * y {sign} {b:.2f}", color=colors[idx % len(colors)], linewidth=2)
                if sign == "≤":
                    ax.fill_between(X, Y, -100, color=colors[idx % len(colors)], alpha=0.15)
                elif sign == "≥":
                    ax.fill_between(X, Y, 100, color=colors[idx % len(colors)], alpha=0.15)

            if feasible:
                ax.scatter(*zip(*feasible), color="red", label="Угловые точки")
                ax.scatter(opt_x, opt_y, color="gold", edgecolor="black", s=200, label="⭐ Оптимум")
                ax.text(opt_x - 2, opt_y - 1, f"Оптимум ({opt_x:.2f}, {opt_y:.2f})", color="orange")

                if abs(a2) > 1e-8:
                    ax.plot(X, (z_opt - a1 * X) / a2, "k--", label=f"Целевая прямая: {a1:.2f}x + {a2:.2f}y = {z_opt:.2f}")

            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 20)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)
            st.pyplot(fig)
            st.markdown("</div>", unsafe_allow_html=True)
