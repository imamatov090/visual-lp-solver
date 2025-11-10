import streamlit as st
import numpy as np
import plotly.graph_objects as go
from itertools import combinations

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

# 💅 CSS — dizayn va ranglar
st.markdown("""
<style>
/* Asosiy CSS qoidalari */
.single-row-container {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 5px 0;
}

.single-row-item {
    flex: 1;
    text-align: center;
}

.number-input {
    width: 80px !important;
    margin: 0 auto !important;
}

/* Segment tugmalar */
.stSegmentedControl label {
    min-width: 60px !important;
    height: 35px !important;
    border-radius: 8px !important;
    border: 1.5px solid #007bff !important;
    background-color: #f8f9fa !important;
    color: #007bff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-weight: 500 !important;
}

.stSegmentedControl label[data-checked="true"] {
    background-color: #007bff !important;
    color: white !important;
}

/* Tugmalar */
.stButton > button {
    background-color: #007bff !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    font-weight: 500 !important;
    padding: 0.3rem 0.8rem !important;
    font-size: 12px !important;
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
    
    # 🔹 Maqsad funksiyasi - HTML orqali bir qatorda
    st.markdown("""
    <div class="single-row-container">
        <div class="single-row-item">
            <div>4,0</div>
            <div style="font-size: 12px;">*x</div>
        </div>
        <div class="single-row-item" style="flex: 0.2;">+</div>
        <div class="single-row-item">
            <div>3,0</div>
            <div style="font-size: 12px;">*y</div>
        </div>
        <div class="single-row-item" style="flex: 0.2;">→</div>
        <div class="single-row-item" style="flex: 0.8;">
            <div>max</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Haqiqiy inputlar - yashirin
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        a1 = st.number_input("a1", value=4.0, key="a1", format="%.1f", step=0.1, label_visibility="collapsed")
    with col2:
        a2 = st.number_input("a2", value=3.0, key="a2", format="%.1f", step=0.1, label_visibility="collapsed")
    with col3:
        opt_type = st.segmented_control("", ["max", "min"], default="max", key="opt_type")

    st.markdown("### ✏️ Ограничения")

    def add_constraint():
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "sign": "≤", "b": 0.0})

    def remove_constraint(i):
        st.session_state.constraints.pop(i)

    for i, cons in enumerate(st.session_state.constraints):
        # Har bir cheklov uchun HTML ko'rinishi
        st.markdown(f"""
        <div class="single-row-container">
            <div class="single-row-item">
                <div>{cons['c']:.1f}</div>
                <div style="font-size: 11px;">x</div>
            </div>
            <div class="single-row-item" style="flex: 0.1;">+</div>
            <div class="single-row-item">
                <div>{cons['d']:.1f}</div>
                <div style="font-size: 11px;">y</div>
            </div>
            <div class="single-row-item" style="flex: 0.2;">{cons['sign']}</div>
            <div class="single-row-item">
                <div>{cons['b']:.1f}</div>
            </div>
            <div class="single-row-item" style="flex: 0.2;">
                <button>🗑</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Haqiqiy inputlar - yashirin
        cols = st.columns([1, 1, 1, 1, 0.5])
        with cols[0]:
            cons["c"] = st.number_input("c", value=cons["c"], key=f"c{i}", format="%.1f", step=0.1, label_visibility="collapsed")
        with cols[1]:
            cons["d"] = st.number_input("d", value=cons["d"], key=f"d{i}", format="%.1f", step=0.1, label_visibility="collapsed")
        with cols[2]:
            cons["sign"] = st.segmented_control("", ["≤", "≥", "="], default=cons["sign"], key=f"sign{i}")
        with cols[3]:
            cons["b"] = st.number_input("b", value=cons["b"], key=f"b{i}", format="%.1f", step=0.1, label_visibility="collapsed")
        with cols[4]:
            if st.button("🗑", key=f"del{i}"):
                remove_constraint(i)
                st.rerun()

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.button("+ Добавить", on_click=add_constraint, use_container_width=True)
    with col2:
        solve = st.button("Решить", use_container_width=True)
    with col3:
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

        st.session_state.results = st.session_state.results[-4:]
        result_id = len(st.session_state.results) + 1
        st.session_state.results.append({
            "№": result_id,
            "x": round(ox, 1),
            "y": round(oy, 1),
            "z": round(zopt, 1),
            "type": opt_type
        })
        
        st.success(f"✅ Решение найдено: x = {ox:.1f}, y = {oy:.1f}, f(x,y) = {zopt:.1f}")
    else:
        st.error("❌ Решение не найдено. Проверьте ограничения.")

    # Grafik chizish
    if feas:
        fig = go.Figure()
        colors = ["rgba(0,123,255,0.3)", "rgba(255,152,0,0.3)", "rgba(156,39,176,0.3)"]

        for i, (c, d, b, sign) in enumerate(lines):
            Y = (b - c * X) / d
            fig.add_trace(go.Scatter(
                x=X, y=Y, mode="lines",
                line=dict(color=colors[i % len(colors)].replace("0.3", "1.0"), width=2),
                fill="tonexty" if sign in ["≤", "≥"] else None,
                fillcolor=colors[i % len(colors)],
                name=f"{c:.1f}x + {d:.1f}y {sign} {b:.1f}"
            ))

        # Optimallik chizig'i
        z_line = zopt
        x_split = ox
        X_left = X[X <= x_split]
        X_right = X[X >= x_split]
        Y_left = (z_line - a1 * X_left) / a2
        Y_right = (z_line - a1 * X_right) / a2

        fig.add_trace(go.Scatter(x=X_left, y=Y_left, mode="lines", line=dict(color="blue", width=3, dash="dot"), name="Min"))
        fig.add_trace(go.Scatter(x=X_right, y=Y_right, mode="lines", line=dict(color="red", width=3, dash="dot"), name="Max"))
        fig.add_trace(go.Scatter(x=[ox], y=[oy], mode="markers+text", text=[f"({ox:.1f},{oy:.1f})"], textposition="top center", marker=dict(color="gold", size=12), name="Оптимум"))

        fig.update_layout(title="График решения", xaxis_title="x", yaxis_title="y", height=500)
        st.plotly_chart(fig, use_container_width=True)

# --- Natijalar --- #
if st.session_state.results:
    st.markdown("### 🧮 История решений")
    for res in reversed(st.session_state.results):
        color = "red" if res["type"] == "max" else "blue"
        bg = "rgba(255,0,0,0.1)" if res["type"] == "max" else "rgba(0,123,255,0.1)"
        
        st.markdown(f"""
        <div style='background:{bg}; border-left:5px solid {color}; border-radius:10px; padding:0.8rem; margin:0.5rem 0;'>
            <b>f(x,y)</b> = {res['z']} &nbsp; при &nbsp; (x = {res['x']}, y = {res['y']}) &nbsp; <b>Тип:</b> {res['type'].upper()}
        </div>
        """, unsafe_allow_html=True)
