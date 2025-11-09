import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# --- Sahifa sozlamalari ---
st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# --- CSS (dizayn va tuzilma) ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 0.5rem;
            max-width: 1300px;
        }
        h1 {
            font-size: 1.4rem;
            text-align: center;
        }
        h3 {
            font-size: 1rem;
        }
        /* 🔹 Number input — ixcham */
        .stNumberInput > div > div > input {
            width: 60px !important;
            font-size: 0.8rem !important;
            padding: 2px 3px !important;
        }
        /* 🔹 Selectbox (≤, ≥, =) belgilarini ko‘rsatish uchun */
        .stSelectbox > div > div > select {
            height: 28px !important;
            font-size: 1rem !important;
            color: black !important;
            text-align: center !important;
            background-color: #ffffff !important;
            border: 1px solid #ccc !important;
            border-radius: 4px !important;
        }
        .stSelectbox > div > div {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        /* 🔹 Tugmalar */
        .stButton>button {
            padding: 0.3rem 0.7rem;
            font-size: 0.8rem;
            border-radius: 6px;
            background-color: #007bff;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .caption-text {
            font-size: 0.75rem;
            color: gray;
        }
        /* 🔹 Chap panelni joylash */
        [data-testid="stVerticalBlock"] > div:first-child {
            margin-left: -30px;
        }
        /* 🔹 Card-style dizayn */
        .stCard {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 3px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sarlavha ---
st.markdown("<h1>📊 Линейное программирование — Решатель</h1>", unsafe_allow_html=True)
st.caption("Интерактивная визуализация и решение задач линейного программирования (2 переменные)")

# --- Ustunlar (chap va o‘ng panel) ---
col_left, col_right = st.columns([1, 1.8])

# ===== CHAP PANEL =====
with col_left:
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("### 🎯 Целевая функция")
    c1, c2, c3, c4 = st.columns([1, 0.3, 1, 0.6])
    with c1:
        a1 = st.number_input("", value=5.3, key="a1")
    with c2:
        st.markdown("*x +*")
    with c3:
        a2 = st.number_input("", value=-7.1, key="a2")
    with c4:
        opt_type = st.selectbox("", ["max", "min"], key="opt")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.markdown("### ✏️ Ограничения")

    # Dastlabki qiymatlar
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
        cols = st.columns([1, 0.3, 1, 0.3, 0.7, 0.7, 0.2])
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}")
        with cols[1]:
            st.markdown("*x +*")
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}")
        with cols[3]:
            st.markdown("*y*")
        with cols[4]:
            cons["sign"] = st.selectbox("", ["≤", "≥", "="],
                index=["≤", "≥", "="].index(cons["sign"]), key=f"sign{i}")
        with cols[5]:
            cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}")
        with cols[6]:
            st.button("🗑", key=f"del{i}", on_click=remove_constraint, args=(i,))

    st.button("+ Добавить", on_click=add_constraint)
    st.markdown("<p class='caption-text'>Коэффициенты можно вводить целыми или дробными (запятая/точка).</p>", unsafe_allow_html=True)

    cA, cB, cC = st.columns(3)
    solve = cA.button("Решить")
    clear = cB.button("Очистить")
    pdf = cC.button("Скачать отчёт (PDF)")

    if clear:
        st.session_state.constraints = []
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ===== O‘NG PANEL =====
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

        points = []
        for l1, l2 in combinations(lines, 2):
            p = intersect(l1, l2)
            if p and -50 < p[0] < 50 and -50 < p[1] < 50:
                points.append(p)

        feasible = []
        for (x, y) in points:
            ok = True
            for (c, d, b, sign) in lines:
                val = c*x + d*y
                if (sign=="≤" and val>b+1e-6) or (sign=="≥" and val<b-1e-6) or (sign=="=" and abs(val-b)>1e-6):
                    ok=False;break
            if ok: feasible.append((x, y))

        if feasible:
            z_vals=[a1*x+a2*y for x,y in feasible]
            best=np.argmax(z_vals) if opt_type=="max" else np.argmin(z_vals)
            opt_x,opt_y=feasible[best];z_opt=z_vals[best]
        else:
            opt_x,opt_y,z_opt=None,None,None

        # --- Grafik ---
        fig, ax = plt.subplots(figsize=(7, 4.3))
        colors=['#007bff','#ff9800','#9c27b0','#4caf50','#f44336','#795548','#00bcd4']
        for i,(c,d,b,sign) in enumerate(lines):
            Y=(b-c*X)/d
            ax.plot(X,Y,label=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}",color=colors[i%len(colors)],lw=1.4)
            if sign=="≤": ax.fill_between(X,Y,-100,color=colors[i%len(colors)],alpha=0.12)
            elif sign=="≥": ax.fill_between(X,Y,100,color=colors[i%len(colors)],alpha=0.12)

        if feasible:
            ax.scatter(*zip(*feasible),color="red",s=25,label="Угловые точки")
            ax.scatter(opt_x,opt_y,color="gold",edgecolor="black",s=70,label="⭐ Оптимум")
            ax.text(opt_x-1,opt_y-0.6,f"({opt_x:.2f}, {opt_y:.2f})",fontsize=7,color="orange")
            if abs(a2)>1e-8:
                ax.plot(X,(z_opt-a1*X)/a2,"k--",lw=1,label=f"{a1:.2f}x+{a2:.2f}y={z_opt:.2f}")

        ax.set_xlim(-15,15); ax.set_ylim(-15,20)
        ax.set_xlabel("x",fontsize=8); ax.set_ylabel("y",fontsize=8)
        ax.legend(fontsize=7); ax.grid(True,linestyle="--",alpha=0.4)
        st.pyplot(fig)
