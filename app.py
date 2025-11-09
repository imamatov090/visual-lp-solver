import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from pulp import LpMaximize, LpMinimize, LpProblem, LpVariable, LpStatus

st.set_page_config(page_title="Линейное программирование — Решатель", layout="wide")

st.title("📊 Линейное программирование — Решатель")
st.markdown("Визуализация и решение задачи линейного программирования (2 переменные)")

# --- Левая панель: ввод данных ---
st.sidebar.header("Целевая функция")
a1 = st.sidebar.number_input("Коэффициент при x (a₁)", value=3.0)
a2 = st.sidebar.number_input("Коэффициент при y (a₂)", value=4.0)
opt_type = st.sidebar.selectbox("Тип оптимизации", ["max", "min"])

st.sidebar.header("Ограничения")
st.sidebar.write("Введите коэффициенты для ограничений (≤, ≥, =)")

c1 = st.sidebar.number_input("c₁ (x)", value=2.0)
d1 = st.sidebar.number_input("d₁ (y)", value=1.0)
b1 = st.sidebar.number_input("b₁ (правая часть)", value=8.0)
sign1 = st.sidebar.selectbox("Знак 1", ["≤", "≥", "="], key="sign1")

c2 = st.sidebar.number_input("c₂ (x)", value=1.0)
d2 = st.sidebar.number_input("d₂ (y)", value=2.0)
b2 = st.sidebar.number_input("b₂ (правая часть)", value=10.0)
sign2 = st.sidebar.selectbox("Знак 2", ["≤", "≥", "="], key="sign2")

st.sidebar.info("Можно использовать только 2 ограничения в этой демо-версии")

# --- Модель ---
model = LpProblem(name="LP", sense=LpMaximize if opt_type == "max" else LpMinimize)
x = LpVariable("x", lowBound=0)
y = LpVariable("y", lowBound=0)

# --- Функция добавления ограничения ---
def add_constraint(model, c, d, b, sign):
    if sign == "≤":
        model += c * x + d * y <= b
    elif sign == "≥":
        model += c * x + d * y >= b
    else:
        model += c * x + d * y == b

# --- Добавляем ограничения ---
add_constraint(model, c1, d1, b1, sign1)
add_constraint(model, c2, d2, b2, sign2)

# --- Целевая функция ---
model += a1 * x + a2 * y

# --- Решаем ---
model.solve()

# --- Интерфейс ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Результаты решения")
    st.write(f"**Статус:** {LpStatus[model.status]}")
    st.write(f"**x = {x.value():.2f}**")
    st.write(f"**y = {y.value():.2f}**")
    st.write(f"**Целевая функция (z) = {model.objective.value():.2f}**")

with col2:
    st.subheader("📈 График решения")
    fig, ax = plt.subplots()

    X = np.linspace(0, 20, 400)
    def line(c, d, b):
        return (b - c * X) / d

    y1 = line(c1, d1, b1)
    y2 = line(c2, d2, b2)

    ax.plot(X, y1, label=f"{c1}x + {d1}y {sign1} {b1}")
    ax.plot(X, y2, label=f"{c2}x + {d2}y {sign2} {b2}")

    # Заштрихованная допустимая область
    Y_fill = np.minimum(y1, y2)
    ax.fill_between(X, 0, np.maximum(0, Y_fill), alpha=0.3, color="green", label="Допустимая область")

    # Оптимум
    ax.scatter(x.value(), y.value(), color="red", s=100, label="Оптимум")
    ax.text(x.value()+0.3, y.value(), f"({x.value():.1f}, {y.value():.1f})", color="red")

    ax.set_xlim(0, 20)
    ax.set_ylim(0, 20)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend()
    st.pyplot(fig)

st.caption("Разработано специально для визуального изучения линейного программирования (демо-версия).")
