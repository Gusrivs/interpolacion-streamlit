import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pages.Utilidades.Inputs import ingresar_puntos

st.title("Interpolación de Newton")
st.write("Ingrese los puntos:")
x, y = ingresar_puntos()

def diferencias_divididas(x, y):
    n = len(x)
    tabla = np.zeros((n, n))
    tabla[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            tabla[i][j] = (tabla[i+1][j-1] - tabla[i][j-1]) / (x[i+j] - x[i])
    return tabla

def formato_polinomio(x, coefs):
    terminos = []
    for i in range(len(coefs)):
        c = round(coefs[i], 4)
        if abs(c) < 1e-10:
            continue
        signo = "+" if c > 0 and terminos else ""
        if i == 0:
            terminos.append(f"{c}")
        elif i == 1:
            terminos.append(f"{signo}{c}(x - {x[0]})")
        else:
            producto = "".join([f"(x - {x[k]})" for k in range(i)])
            terminos.append(f"{signo}{c}{producto}")
    return "P(x) = " + " ".join(terminos) if terminos else "P(x) = 0"

def evaluar_newton(x, coefs, xp):
    resultado = coefs[0]
    producto = 1
    for i in range(1, len(coefs)):
        producto *= (xp - x[i-1])
        resultado += coefs[i] * producto
    return resultado

if st.button("Calcular"):
    tabla = diferencias_divididas(x, y)
    coefs = tabla[0, :]
    st.session_state["coefs"] = coefs
    st.session_state["tabla"] = tabla
    st.session_state["x"] = x
    st.session_state["y"] = y

if "coefs" in st.session_state:
    coefs = st.session_state["coefs"]
    tabla = st.session_state["tabla"]
    x_g = st.session_state["x"]
    y_g = st.session_state["y"]
    n = len(x_g)

    # --- Polinomio ---
    st.subheader("Polinomio de Newton")
    st.code(formato_polinomio(x_g, coefs))

    # --- Tabla de diferencias divididas ---
    st.subheader("Tabla de diferencias divididas")

    col_names = ["j", "xᵢ", "f(xᵢ)"]
    for orden in range(1, n):
        nodos = ", ".join([f"x{k}" for k in range(orden + 1)])
        col_names.append(f"f({nodos})")

    filas = []
    for i in range(n):
        fila = [i, x_g[i], round(tabla[i][0], 6)]
        for j in range(1, n):
            if i + j < n:
                fila.append(round(tabla[i][j], 6))
            else:
                fila.append("")
        filas.append(fila)

    df = pd.DataFrame(filas, columns=col_names)
    st.dataframe(df, use_container_width=True)

    # --- Evaluación ---
    st.subheader("Evaluar el polinomio")
    xp = st.number_input("Valor a interpolar (x)")
    if st.button("Evaluar"):
        resultado = evaluar_newton(x_g, coefs, xp)
        st.success(f"P({xp}) = {resultado}")

        # --- Gráfica (igual que Lagrange, con el punto evaluado) ---
        x_vals = np.linspace(min(x_g), max(x_g), 100)
        y_vals = [evaluar_newton(x_g, coefs, xi) for xi in x_vals]

        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals)
        ax.scatter(x_g, y_g)
        ax.scatter(xp, resultado)
        ax.set_title("Polinomio de Interpolación (Newton)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        st.pyplot(fig)