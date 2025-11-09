import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.title("Линейное программирование — визуальный метод")
st.write("Визуализация задачи линейного программирования с двумя переменными (x и y) графическим способом.")

# Целевая функция
st.subheader("Целевая функция: max z = a₁x + a₂y")
a1 = st.number_input("a₁ (коэффициент при x)", value=3.0)
a2 = st.number_input("a₂ (коэффициент при y)", value=4.0)

# Ограничения
st.subheader("Ограничения (в виде ≤):")
c1 = st.number_input("c₁ (коэффициент при x в 1-м ограничении)", value=2.0)
d1 = st.number_input("d₁ (коэффициент при y в 1-м ограничении)", value=1.0)
b1 = st.number_input("b₁ (правая часть 1-го ограничения)", value=8.0)

c2 = st.number_input("c₂ (коэффициент при x во 2-м ограничении)", value=1.0)
d2 = st.number_input("d₂ (коэффициент при y во 2-м ограничении)", value=2.0)
b2 = st.number_input("b₂ (правая часть 2-го ограничения)", value=10.0)

# Построение графика
x = np.linspace(0, 10, 400)
y1 = (b1 - c1 * x) / d1
y2 = (b2 - c2 * x) / d2

fig, ax = plt.subplots()
ax.plot(x, y1, label=f"{c1}x + {d1}y ≤ {b1}")
ax.plot(x, y2, label=f"{c2}x + {d2}y ≤ {b2}")

# Область допустимых решений
y_fill = np.minimum(y1, y2)
y_fill = np.maximum(0, y_fill)
ax.fill_between(x, 0, y_fill, alpha=0.3, color="green", label="Допустимая область")

ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
st.pyplot(fig)
