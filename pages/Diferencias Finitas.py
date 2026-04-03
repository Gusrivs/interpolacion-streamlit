import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
st.set_page_config(page_title="Diferencias Finitas", page_icon="images/Logo.ico", layout="centered")

st.title("Interpolación por Diferencias Finitas")
st.write("Ingrese los parámetros (puntos equiespaciados):")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0

r = st.session_state["reset"]

col1, col2, col3 = st.columns(3)
with col1:
    x0 = st.number_input("x₀ (valor inicial)", value=0.0, key=f"x0_{r}")
with col2:
    h = st.number_input("h (paso)", value=1.0, min_value=0.0001, key=f"h_{r}")
with col3:
    n = int(st.number_input("Cantidad de puntos", min_value=3, step=1, value=4, key=f"n_{r}"))

x = [x0 + i * h for i in range(n)]

st.write("Ingrese los valores de y:")
cols = st.columns(n)
y = []
for i in range(n):
    with cols[i]:
        yi = st.number_input(f"y(x={x[i]:.2f})", key=f"y{i}_{r}", value=0.0)
        y.append(float(yi))

metodo = st.selectbox("Método", ["Stirling", "Bessel"], key=f"metodo_{r}")

def tabla_diferencias(y):
    n = len(y)
    T = np.zeros((n, n))
    T[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            T[i][j] = T[i + 1][j - 1] - T[i][j - 1]
    return T

def evaluar_stirling(T, x, h, xp):
    n = len(x)
    m = n // 2
    s = (xp - x[m]) / h
    resultado = T[m][0]
    if m >= 1 and m - 1 >= 0:
        resultado += s * (T[m][1] + T[m - 1][1]) / 2
    if m - 1 >= 0 and n - 2 > m - 1:
        resultado += (s**2 / math.factorial(2)) * T[m - 1][2]
    if m - 1 >= 1 and m - 2 >= 0:
        coef3 = s * (s**2 - 1) / math.factorial(3)
        resultado += coef3 * (T[m - 1][3] + T[m - 2][3]) / 2
    if m - 2 >= 0 and n - 4 > m - 2:
        coef4 = s**2 * (s**2 - 1) / math.factorial(4)
        resultado += coef4 * T[m - 2][4]
    if m - 2 >= 1 and m - 3 >= 0:
        coef5 = s * (s**2 - 1) * (s**2 - 4) / math.factorial(5)
        resultado += coef5 * (T[m - 2][5] + T[m - 3][5]) / 2
    return resultado

def evaluar_bessel(T, x, h, xp):
    n = len(x)
    m = n // 2 - 1
    s = (xp - x[m]) / h
    resultado = (T[m][0] + T[m + 1][0]) / 2
    resultado += (s - 0.5) * T[m][1]
    if m - 1 >= 0:
        coef2 = s * (s - 1) / math.factorial(2)
        resultado += coef2 * (T[m - 1][2] + T[m][2]) / 2
    if m - 1 >= 0:
        coef3 = (s - 0.5) * s * (s - 1) / math.factorial(3)
        resultado += coef3 * T[m - 1][3]
    if m - 2 >= 0 and m - 1 >= 0:
        coef4 = s * (s - 1) * (s + 1) * (s - 2) / math.factorial(4)
        resultado += coef4 * (T[m - 2][4] + T[m - 1][4]) / 2
    return resultado

if st.button("Calcular tabla"):
    T = tabla_diferencias(y)
    st.session_state["T"]   = T
    st.session_state["x_g"] = x
    st.session_state["y_g"] = y
    st.session_state["h_g"] = h

if "T" not in st.session_state:
    st.stop()

T   = st.session_state["T"]
x_g = st.session_state["x_g"]
y_g = st.session_state["y_g"]
h_g = st.session_state["h_g"]
n_g = len(x_g)

superindices = {1:'¹', 2:'²', 3:'³', 4:'⁴', 5:'⁵', 6:'⁶', 7:'⁷', 8:'⁸', 9:'⁹'}

st.subheader("Tabla de diferencias finitas")
col_names = ["i", "xᵢ", "yᵢ"] + [f"Δ{superindices.get(j, str(j))}y" for j in range(1, n_g)]

filas = []
for i in range(n_g):
    fila = [i, round(x_g[i], 4), round(T[i][0], 6)]
    for j in range(1, n_g):
        fila.append(round(float(T[i][j]), 6) if i + j < n_g else "")
    filas.append(fila)

df = pd.DataFrame(filas, columns=col_names).astype(object)
st.dataframe(df, width='stretch')

if metodo == "Stirling":
    m = n_g // 2
    st.info(f"Stirling: nodo central  x_{m} = {x_g[m]:.4f}")
else:
    m = n_g // 2 - 1
    st.info(f"Bessel: interpolación entre  x_{m} = {x_g[m]:.4f}  y  x_{m+1} = {x_g[m+1]:.4f}")

st.subheader("Evaluar el polinomio")
xp = st.number_input("Valor a interpolar (xₚ)", key=f"xp_{r}")

if metodo == "Stirling":
    m = n_g // 2
    s_preview = (xp - x_g[m]) / h_g
    if abs(s_preview) > 1:
        st.warning(f"⚠️ s = {s_preview:.3f}. Stirling es más preciso cuando |s| ≤ 1 (xₚ cerca del nodo central).")
else:
    m = n_g // 2 - 1
    s_preview = (xp - x_g[m]) / h_g
    if not (0.25 <= s_preview <= 0.75):
        st.warning(f"⚠️ s = {s_preview:.3f}. Bessel es más preciso cuando 0.25 ≤ s ≤ 0.75.")

if st.button("Evaluar"):
    try:
        if metodo == "Stirling":
            resultado = evaluar_stirling(T, x_g, h_g, xp)
            m = n_g // 2
        else:
            resultado = evaluar_bessel(T, x_g, h_g, xp)
            m = n_g // 2 - 1

        s_val = (xp - x_g[m]) / h_g
        st.success(f"P({xp}) ≈ {resultado:.6f}")
        st.caption(f"s = (xₚ − x_central) / h = ({xp} − {x_g[m]:.4f}) / {h_g:.4f} = {s_val:.4f}")

        x_vals = np.linspace(min(x_g), max(x_g), 300)
        if metodo == "Stirling":
            y_vals = [evaluar_stirling(T, x_g, h_g, xi) for xi in x_vals]
        else:
            y_vals = [evaluar_bessel(T, x_g, h_g, xi) for xi in x_vals]

        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals, label="Polinomio interpolante")
        ax.scatter(x_g, y_g, zorder=5, label="Puntos dados")
        ax.scatter(xp, resultado, color="red", zorder=6,
                   label=f"P({xp}) = {resultado:.4f}")
        ax.set_title(f"Interpolación por Diferencias Finitas ({metodo})")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.legend()
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al evaluar: {e}")

st.divider()
if st.button("Limpiar"):
    reset_val = st.session_state["reset"] + 1
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state["reset"] = reset_val
    st.rerun()