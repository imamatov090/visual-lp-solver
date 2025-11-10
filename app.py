import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# 💅 CSS — dizayn va ranglar
st.markdown("""
<style>
/* Segment tugmalar */
.stSegmentedControl label {
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
    white-space: nowrap !important;
}
.stSegmentedControl label[data-checked="true"] {
    background-color: #007bff !important;
    color: white !important;
    box-shadow: 0 0 6px rgba(0,123,255,0.4);
}

/* Tugmalar */
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

/* Удалить */
button[kind="secondary"] {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 6px !important;
}
button[kind="secondary"]:hover {
    background-color: #0056b3 !important;
}

/* Gradient tarix kartochkasi */
.result-card {
    background: linear-gradient(90deg, rgba(0,123,255,0.15) 0%, rgba(0,212,255,0.15) 100%);
    border-left: 5px solid #007bff;
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-top: 0.8rem;
    font-size: 15px;
}

/* ✅ YANGI: Inputlarni markazlashtirish */
.stNumberInput > div > div {
    text-align: center;
}

/* ✅ YANGI: Tugmalarni kichikroq qilish */
.stButton > button {
    padding: 0.25rem 0.5rem !important;
    font-size: 12px !important;
}

/* ✅ YANGI: Segment control markazida */
.stSegmentedControl {
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)

# --- Session state initialization --- #
if "constraints" not in st.session_state:
    st.session_state.constraints = [
        {"c": 3.2, "d": -2.0, "sign": "≤", "b": 3.0},
        {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
    ]

if "results" not in st.session_state:
    st.session_state.results = []

# --- Sidebar --- #
with st.sidebar:
    st.markdown("### 🎯 Целевая функция")
    
    # 🔹 BIR QATORDA: 4,0 *x + 3,0 *y → max
    col1, col2, col3, col4, col5, col6 = st.columns([1.2, 0.2, 1.2, 0.2, 0.8, 1.2])
    
    with col1:
        a1 = st.number_input("", value=4.0, key="a1", format="%.1f", step=0.1, label_visibility="collapsed")
        st.markdown("<div style='text-align: center; margin-top: -10px; font-size: 12px;'>*x</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='text-align: center; margin-top: 8px; font-size: 14px;'>+</div>", unsafe_allow_html=True)
    
    with col3:
        a2 = st.number_input("", value=3.0, key="a2", format="%.1f", step=0.1, label_visibility="collapsed")
        st.markdown("<div style='text-align: center; margin-top: -10px; font-size: 12px;'>*y</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div style='text-align: center; margin-top: 8px; font-size: 14px;'>→</div>", unsafe_allow_html=True)
    
    with col5:
        st.write("")
    
    with col6:
        st.markdown("<div style='margin-top: -5px;'>", unsafe_allow_html=True)
        opt_type = st.segmented_control(
            "",
            ["max", "min"],
            selection_mode="single",
            default="max",
            key="opt_type"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### ✏️ Ограничения")

    if "constraints" not in st.session_state:
        st.session_state.constraints = [
            {"c": 3.2, "d": -2.0, "sign": "≤", "b": 3.0},
            {"c": 1.6, "d": 2.3, "sign": "≤", "b": -5.0},
        ]

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})

    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    for i, cons in enumerate(st.session_state.constraints):
        # 🔹 BIR QATORDA: 3,2 x + -2,0 y ≤ 3,0 🗑
        cols = st.columns([1.2, 0.2, 1.2, 0.2, 0.8, 1.2, 0.4])
        
        with cols[0]:
            cons["c"] = st.number_input("", value=cons["c"], key=f"c{i}", format="%.1f", step=0.1, label_visibility="collapsed")
            st.markdown("<div style='text-align: center; margin-top: -10px; font-size: 11px;'>x</div>", unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("<div style='text-align: center; margin-top: 8px; font-size: 12px;'>+</div>", unsafe_allow_html=True)
        
        with cols[2]:
            cons["d"] = st.number_input("", value=cons["d"], key=f"d{i}", format="%.1f", step=0.1, label_visibility="collapsed")
            st.markdown("<div style='text-align: center; margin-top: -10px; font-size: 11px;'>y</div>", unsafe_allow_html=True)
        
        with cols[3]:
            st.markdown("<div style='text-align: center; margin-top: 8px; font-size: 12px;'></div>", unsafe_allow_html=True)
        
        with cols[4]:
            cons["sign"] = st.segmented_control(
                "",
                ["≤", "≥", "="],
                selection_mode="single",
                default=cons["sign"],
                key=f"sign{i}"
            )
        
        with cols[5]:
            cons["b"] = st.number_input("", value=cons["b"], key=f"b{i}", format="%.1f", step=0.1, label_visibility="collapsed")
            st.markdown("<div style='text-align: center; margin-top: -10px; font-size: 11px; color: transparent;'>.</div>", unsafe_allow_html=True)
        
        with cols[6]:
            st.markdown("<div style='margin-top: -5px;'>", unsafe_allow_html=True)
            if st.button("🗑", key=f"del{i}"):
                remove_constraint(i)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # Tugmalar
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        st.button("+ Добавить", on_click=add_constraint, use_container_width=True)
    with col_btn2:
        solve = st.button("Решить", use_container_width=True)
    with col_btn3:
        if st.button("Очистить", use_container_width=True):
            st.session_state.constraints = []
            st.session_state.results = []
            st.rerun()

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
            "x": round(ox, 1),
            "y": round(oy, 1),
            "z": round(zopt, 1),
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
            name=f"{c:.1f}x + {d:.1f}y {sign} {b:.1f}"
        ))

    # 🔹 Целевая прямая — ikki rangli (qizil / ko‘k)
    if feas:
        z_line = zopt
        x_split = ox
        y_split = (z_line - a1 * x_split) / a2

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
            text=[f"({ox:.1f},{oy:.1f})"],
            textposition="top center",
            marker=dict(color="gold", size=12, line=dict(color="black", width=1)),
            name="⭐ Оптимум"
        ))

    # 🔳 Setka — kichikroq oraliqda (har 2 birlikda)
    fig.update_layout(
        title="График решения",
        xaxis_title="x",
        yaxis_title="y",
        height=500,
        template="plotly_white",
        xaxis=dict(showgrid=True, gridwidth=0.6, gridcolor="LightGray", dtick=2),
        yaxis=dict(showgrid=True, gridwidth=0.6, gridcolor="LightGray", dtick=2)
    )

    st.plotly_chart(fig, use_container_width=True)

# --- Natijalar --- #
if st.session_state.results:
    st.markdown("### 🧮 История решений (значения функции)")

    for res in reversed(st.session_state.results):
        if res["type"] == "max":
            bg_color = "rgba(255, 0, 0, 0.1)"
            border_color = "red"
        else:
            bg_color = "rgba(0, 123, 255, 0.1)"
            border_color = "blue"

        st.markdown(
            f"<div style='background:{bg_color}; border-left:5px solid {border_color}; "
            f"border-radius:10px; padding:0.8rem 1rem; margin-top:0.8rem; font-size:15px;'>"
            f"<b>f<sub>{res['№']}</sub>(x, y)</b> = {res['z']} &nbsp;&nbsp; "
            f"<i>при</i> (x = {res['x']}, y = {res['y']}) &nbsp;&nbsp; "
            f"<b>Тип:</b> {res['type'].upper()}"
            f"</div>",
            unsafe_allow_html=True
        )
