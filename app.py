import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# --- Sahifa sozlamalari ---
st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- Sidebar (chap panel) ---
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")
    a1 = st.number_input("Коэффициент при x", value=5.3, key="a1")
    a2 = st.number_input("Коэффициент при y", value=-7.1, key="a2")

    opt_type = st.radio("Тип оптимизации:", ["max", "min"], horizontal=True)

    st.markdown("### ✏️ Ограничения")

    # Cheklovlarni boshlang'ich qiymatlar bilan yaratamiz
    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "=", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
            {"c": 3.2, "d": -6.0, "sign": "≥", "b": 7.0},
            {"c": 7.0, "d": -2.0, "sign": "≤", "b": 10.0},
        ]

    # Qo‘shish va o‘chirish funksiyalari
    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})
    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    # Cheklovlarni kiritish qismi
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

# --- O‘ng tomon (grafik) ---
st.title("📊 Визуализация решения задачи линейного программирования")

if solve:
    X = np.linspace(-20, 20, 600)
    lines = []
    for cons in st.session_state.constraints:
        c, d, b, sign = cons["c"], cons["d"], cons["b"], cons["sign"]
        if abs(d) < 1e-8:
            continue
        lines.append((c, d, b, sign))

    # Ikki to‘g‘ri chiziqning kesishish nuqtasi
    def intersect(l1, l2):
        (a1, b1, c1, _), (a2, b2, c2, _) = l1, l2
        det = a1*b2 - a2*b1
        if abs(det) < 1e-8:
            return None
        x = (c1*b2 - c2*b1)/det
        y = (a1*c2 - a2*c1)/det
        return (x, y)

    # Barcha kesishish nuqtalarini topamiz
    pts = []
    for l1, l2 in combinations(lines, 2):
        p = intersect(l1, l2)
        if p and -50 < p[0] < 50 and -50 < p[1] < 50:
            pts.append(p)

    # Yaroqli nuqtalarni topamiz
    feas = []
    for (x, y) in pts:
        ok = True
        for (c, d, b, sign) in lines:
            val = c*x + d*y
            if (sign=="≤" and val>b) or (sign=="≥" and val<b) or (sign=="=" and abs(val-b)>1e-6):
                ok=False; break
        if ok:
            feas.append((x, y))

    # Optimal yechim
    if feas:
        z = [a1*x + a2*y for (x, y) in feas]
        best = np.argmax(z) if opt_type=="max" else np.argmin(z)
        ox, oy, zopt = *feas[best], z[best]
    else:
        ox = oy = zopt = None

    # --- Grafik chizamiz ---
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ['#007bff','#ff9800','#9c27b0','#4caf50','#f44336','#795548','#00bcd4']

    for i,(c,d,b,sign) in enumerate(lines):
        Y = (b - c*X) / d
        ax.plot(X, Y, color=colors[i%len(colors)], lw=1.4,
                label=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}")
        if sign=="≤":
            ax.fill_between(X, Y, -100, color=colors[i%len(colors)], alpha=.12)
        elif sign=="≥":
            ax.fill_between(X, Y, 100, color=colors[i%len(colors)], alpha=.12)

    if feas:
        ax.scatter(*zip(*feas), c="red", s=25, label="Угловые точки")
        ax.scatter(ox, oy, c="gold", edgecolor="black", s=70, label="⭐ Оптимум")
        ax.text(ox-1, oy-.6, f"({ox:.2f}, {oy:.2f})", fontsize=7, color="orange")
        if abs(a2)>1e-8:
            ax.plot(X, (zopt - a1*X)/a2, "k--", lw=1, label=f"{a1:.2f}x+{a2:.2f}y={zopt:.2f}")

    ax.set_xlim(-15, 15)
    ax.set_ylim(-15, 20)
    ax.set_xlabel("x", fontsize=8)
    ax.set_ylabel("y", fontsize=8)
    ax.legend(fontsize=7)
    ax.grid(True, ls="--", alpha=.4)
    st.pyplot(fig)
