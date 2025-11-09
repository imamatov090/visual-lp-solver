import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# Sahifa sozlamalari
st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- CSS dizayn ---
st.markdown("""
<style>
h1 {text-align:center;}
.block-container {max-width:1400px; padding-top:0.5rem;}
/* ixcham inputlar */
.stNumberInput > div > div > input {
    width: 60px !important;
    font-size: 0.8rem !important;
    padding: 2px 4px !important;
}
/* radio label ixcham */
.stRadio label {font-size: 0.85rem !important;}
/* tugmalar */
.stButton>button {
    padding: 0.25rem 0.6rem;
    font-size: 0.8rem;
    border-radius: 6px;
    background-color: #007bff;
    color: white;
    border: none;
}
.stButton>button:hover {background-color:#0056b3;}
/* trash tugma */
button[kind="secondary"] {
    background-color: #ff4d4d !important;
    color: white !important;
    border: none !important;
}
button[kind="secondary"]:hover {background-color: #c9302c !important;}
</style>
""", unsafe_allow_html=True)

# --- Sarlavha ---
st.markdown("<h1>📊 Линейное программирование — Решатель</h1>", unsafe_allow_html=True)
st.caption("Интерактивная визуализация и решение задач линейного программирования (2 переменные)")

# Chap va o‘ng tomonni aniqlaymiz
col_left, col_right = st.columns([0.85, 1.15], gap="large")

# === CHAP PANEL ===
with col_left:
    st.markdown("### 🎯 Целевая функция")
    c1, c2, c3 = st.columns([1, 0.25, 1])
    with c1:
        a1 = st.number_input("", value=5.3, key="a1")
    with c2:
        st.markdown("x +")
    with c3:
        a2 = st.number_input("", value=-7.1, key="a2")

    opt_type = st.radio("Тип оптимизации:", ["max", "min"], horizontal=True)

    st.markdown("### ✏️ Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "=", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
            {"c": 3.2, "d": -6.0, "sign": "≥", "b": 7.0},
            {"c": 7.0, "d": -2.0, "sign": "≤", "b": 10.0},
            {"c": -6.5, "d": 3.0, "sign": "≤", "b": 9.0},
        ]

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})

    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    # Har bir cheklov uchun qator
    for i, cons in enumerate(st.session_state.constraints):
        c = st.columns([1, .25, 1, .35, 1.1, .9, .25])
        with c[0]: cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}")
        with c[1]: st.markdown("x +")
        with c[2]: cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}")
        with c[3]: st.markdown("y")
        with c[4]:
            cons["sign"] = st.radio(
                "", ["≤", "≥", "="],
                index=["≤", "≥", "="].index(cons["sign"]),
                horizontal=True, key=f"sign{i}"
            )
        with c[5]: cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}")
        with c[6]:
            if st.button("🗑", key=f"del{i}", type="secondary"):
                remove_constraint(i)
                st.experimental_rerun()

    st.button("+ Добавить", on_click=add_constraint)
    cA, cB, cC = st.columns(3)
    solve = cA.button("Решить")
    clear = cB.button("Очистить")
    if clear:
        st.session_state.constraints = []
        st.experimental_rerun()

# === O‘NG PANEL (GRAFIK) ===
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
            det = a1*b2 - a2*b1
            if abs(det) < 1e-8: return None
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
                if (sign=="≤" and val>b) or (sign=="≥" and val<b) or (sign=="=" and abs(val-b)>1e-6):
                    ok=False; break
            if ok: feas.append((x, y))

        if feas:
            z = [a1*x + a2*y for (x, y) in feas]
            best = np.argmax(z) if opt_type=="max" else np.argmin(z)
            ox, oy, zopt = *feas[best], z[best]
        else:
            ox = oy = zopt = None

        fig, ax = plt.subplots(figsize=(6.8, 4.4))
        colors = ['#007bff','#ff9800','#9c27b0','#4caf50','#f44336','#795548','#00bcd4']
        for i,(c,d,b,sign) in enumerate(lines):
            Y = (b - c*X) / d
            ax.plot(X, Y, color=colors[i%len(colors)], lw=1.4,
                    label=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}")
            if sign=="≤": ax.fill_between(X, Y, -100, color=colors[i%len(colors)], alpha=.12)
            elif sign=="≥": ax.fill_between(X, Y, 100, color=colors[i%len(colors)], alpha=.12)

        if feas:
            ax.scatter(*zip(*feas), c="red", s=25, label="Угловые точки")
            ax.scatter(ox, oy, c="gold", edgecolor="black", s=70, label="⭐ Оптимум")
            ax.text(ox-1, oy-.6, f"({ox:.2f}, {oy:.2f})", fontsize=7, color="orange")
            if abs(a2)>1e-8:
                ax.plot(X, (zopt - a1*X)/a2, "k--", lw=1, label=f"{a1:.2f}x+{a2:.2f}y={zopt:.2f}")

        ax.set_xlim(-15, 15); ax.set_ylim(-15, 20)
        ax.set_xlabel("x", fontsize=8); ax.set_ylabel("y", fontsize=8)
        ax.legend(fontsize=7); ax.grid(True, ls="--", alpha=.4)
        st.pyplot(fig)
