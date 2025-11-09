import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pulp import LpProblem, LpVariable, LpMaximize, LpMinimize, LpStatus
from fpdf import FPDF

# --- Настройки страницы ---
st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Линейное программирование — Решатель</h1>", unsafe_allow_html=True)
st.caption("Интерактивное визуальное решение задачи линейного программирования (2 переменные)")

# --- Целевая функция ---
st.subheader("Целевая функция")
col_obj = st.columns([1, 1, 0.6])
with col_obj[0]:
    a1 = st.number_input("a₁ (коэффициент при x)", value=3.0)
with col_obj[1]:
    a2 = st.number_input("a₂ (коэффициент при y)", value=4.0)
with col_obj[2]:
    opt_type = st.selectbox("Тип оптимизации", ["max", "min"])

# --- Ограничения ---
st.subheader("Ограничения")
st.caption("Добавляйте или удаляйте ограничения (≤, ≥, =). Можно вводить до 10 штук.")

if "constraints" not in st.session_state:
    st.session_state.constraints = [{"c": 2.0, "d": 1.0, "b": 8.0, "sign": "≤"}]

def add_constraint():
    if len(st.session_state.constraints) < 10:
        st.session_state.constraints.append({"c": 1.0, "d": 1.0, "b": 5.0, "sign": "≤"})
    else:
        st.warning("Максимум 10 ограничений!")

def remove_constraint(i):
    st.session_state.constraints.pop(i)

# Отображение ограничений
for i, cons in enumerate(st.session_state.constraints):
    cols = st.columns([1, 1, 1, 0.8, 0.3])
    with cols[0]:
        cons["c"] = st.number_input(f"c{i+1} (x)", value=cons["c"], key=f"cx{i}")
    with cols[1]:
        cons["d"] = st.number_input(f"d{i+1} (y)", value=cons["d"], key=f"dy{i}")
    with cols[2]:
        cons["b"] = st.number_input(f"b{i+1}", value=cons["b"], key=f"b{i}")
    with cols[3]:
        cons["sign"] = st.selectbox("Знак", ["≤", "≥", "="], index=["≤", "≥", "="].index(cons["sign"]), key=f"sign{i}")
    with cols[4]:
        st.button("❌", key=f"del{i}", on_click=remove_constraint, args=(i,))

st.button("+ Добавить ограничение", on_click=add_constraint)

# --- Кнопки ---
col_btns = st.columns([1, 1, 1])
solve = col_btns[0].button("🧮 Решить")
clear = col_btns[1].button("🧹 Очистить")
export_pdf = col_btns[2].button("📄 Скачать отчёт (PDF)")

if clear:
    st.session_state.constraints = [{"c": 2.0, "d": 1.0, "b": 8.0, "sign": "≤"}]
    st.experimental_rerun()

# --- Решение задачи ---
if solve:
    model = LpProblem("LP", LpMaximize if opt_type == "max" else LpMinimize)
    x = LpVariable("x", lowBound=0)
    y = LpVariable("y", lowBound=0)

    # Целевая функция
    model += a1 * x + a2 * y

    # Добавляем ограничения
    for cons in st.session_state.constraints:
        c, d, b, sign = cons["c"], cons["d"], cons["b"], cons["sign"]
        if sign == "≤":
            model += c * x + d * y <= b
        elif sign == "≥":
            model += c * x + d * y >= b
        else:
            model += c * x + d * y == b

    model.solve()

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📋 Результаты решения")
        st.write(f"**Статус:** {LpStatus[model.status]}")
        st.write(f"**x = {x.value():.2f}**")
        st.write(f"**y = {y.value():.2f}**")
        st.write(f"**Целевая функция (z) = {model.objective.value():.2f}**")

    with col2:
        st.subheader("📈 График решения")

        fig, ax = plt.subplots(figsize=(10, 7))
        X = np.linspace(-10, 20, 800)
        colors = ['blue', 'orange', 'purple', 'green', 'red', 'brown', 'cyan', 'magenta', 'gray', 'olive']

        for idx, cons in enumerate(st.session_state.constraints):
            c, d, b, sign = cons["c"], cons["d"], cons["b"], cons["sign"]
            if abs(d) < 1e-8:
                continue
            Y = (b - c * X) / d
            ax.plot(X, Y, label=f"{c:.2f}x + {d:.2f}y {sign} {b:.2f}", color=colors[idx % len(colors)])

        # Оптимум
        if x.value() is not None and y.value() is not None:
            ax.scatter(x.value(), y.value(), color="gold", s=150, edgecolor="black", label="⭐ Оптимум")
            ax.text(x.value()+0.5, y.value()+0.5, f"({x.value():.2f}, {y.value():.2f})", color="red")

        ax.set_xlim(-10, 20)
        ax.set_ylim(-10, 20)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        st.pyplot(fig)

    # --- PDF отчёт ---
    if export_pdf:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Отчёт по задаче линейного программирования", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Тип оптимизации: {opt_type}", ln=True)
        pdf.cell(200, 10, txt=f"Целевая функция: z = {a1}x + {a2}y", ln=True)
        pdf.cell(200, 10, txt=f"x = {x.value():.2f}, y = {y.value():.2f}, z = {model.objective.value():.2f}", ln=True)
        pdf.output("report.pdf")
        with open("report.pdf", "rb") as f:
            st.download_button("⬇️ Скачать отчёт (PDF)", f, "report.pdf")
