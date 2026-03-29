import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
st.title("Interpolación de Lagrange")
st.write("Ingrese los puntos:")
n = st.number_input("Cantidad de puntos", min_value=2, step=1)
x = []
y = []
for i in range(n):
    col1, col2 = st.columns(2)
    with col1:
        xi = st.number_input(f"x{i}", key=f"x{i}")
    with col2:
        yi = st.number_input(f"y{i}", key=f"y{i}")
    x.append(xi)
    y.append(yi)
xp = st.number_input("Valor a interpolar (x)")
def lagrange(x, y, xp):
    n = len(x)
    yp = 0
    for i in range(n):
        li = 1
        for j in range(n):
            if i != j:
                li *= (xp - x[j]) / (x[i] - x[j])
        yp += y[i] * li
    return yp
if st.button("Calcular"):
    resultado = lagrange(x, y, xp)
    st.success(f"Resultado: {resultado}")
    x_vals = np.linspace(min(x), max(x), 100)
    y_vals = [lagrange(x, y, xi) for xi in x_vals]
    fig, ax = plt.subplots()
    ax.plot(x_vals, y_vals)
    ax.scatter(x, y)
    ax.scatter(xp, resultado)
    ax.set_title("Polinomio de Interpolación (Lagrange)")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    st.pyplot(fig)