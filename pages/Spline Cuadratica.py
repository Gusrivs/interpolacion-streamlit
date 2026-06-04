import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Spline Cuadrática", page_icon="images/Logo.ico", layout="centered")
st.title("Interpolación por Spline Cuadrática")
st.write("Ingrese los puntos para construir los splines cuadráticos:")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0

x = []
y = []

modo = st.selectbox("Modo de ingreso", ["Manual", "Cargar desde Excel"], index=None)

if modo == "Cargar desde Excel":
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"], key=f"file_uploader_{st.session_state['reset']}")
    st.caption("El archivo debe tener columnas nombradas: x, y")
    if archivo:
        df = pd.read_excel(archivo)
        df = df.sort_values("x").reset_index(drop=True)
        x = df["x"].tolist()
        y = df["y"].tolist()
        n = len(x)
        st.success(f"{n} puntos cargados correctamente")
        st.dataframe(df, use_container_width=True)

if modo == "Manual":
    n = int(st.number_input("Cantidad de puntos", min_value=3, step=1, value=3,
                            key=f"n_{st.session_state['reset']}"))
    for i in range(n):
        st.markdown(f"**Punto {i}**")
        col1, col2 = st.columns(2)
        with col1:
            xi = st.number_input(f"x{i}", key=f"x{i}_{st.session_state['reset']}", value=0.0)
        with col2:
            yi = st.number_input(f"y{i}", key=f"y{i}_{st.session_state['reset']}", value=0.0)
        x.append(float(xi))
        y.append(float(yi))


def spline_cuadratica(x, y):
    n = len(x)
    m = n - 1
    size = 3 * m
    A = np.zeros((size, size))
    b_vec = np.zeros(size)
    eq = 0
    for i in range(m):
        hi = x[i + 1] - x[i]
        A[eq][3 * i + 2] = 1
        b_vec[eq] = y[i]
        eq += 1
        A[eq][3 * i]     = hi ** 2
        A[eq][3 * i + 1] = hi
        A[eq][3 * i + 2] = 1
        b_vec[eq] = y[i + 1]
        eq += 1
    for i in range(m - 1):
        hi = x[i + 1] - x[i]
        A[eq][3 * i]     =  2 * hi
        A[eq][3 * i + 1] =  1
        A[eq][3 * i + 4] = -1
        b_vec[eq] = 0
        eq += 1
    A[eq][0] = 1
    b_vec[eq] = 0
    try:
        coefs = np.linalg.solve(A, b_vec)
    except np.linalg.LinAlgError:
        return None
    splines = []
    for i in range(m):
        a = coefs[3 * i]
        b = coefs[3 * i + 1]
        c = coefs[3 * i + 2]
        splines.append((a, b, c, x[i], x[i + 1]))
    return splines


def evaluar_spline(splines, xp):
    for (a, b, c, xi, xi1) in splines:
        if xi <= xp <= xi1:
            t = xp - xi
            return a * t ** 2 + b * t + c
    return None


if st.button("Calcular"):
    if len(x) < 3:
        st.error("⚠️ Se necesitan al menos 3 puntos.")
    elif len(set(round(xi, 10) for xi in x)) != len(x):
         st.error("⚠️ Todos los puntos deben tener x distintos.")
    else:
        # Ordenar por x
        pares = sorted(zip(x, y), key=lambda p: p[0])
        x_ord = [p[0] for p in pares]
        y_ord = [p[1] for p in pares]
        splines = spline_cuadratica(x_ord, y_ord)
        if splines is None:
            st.error("⚠️ El sistema no tiene solución. Verificá que los puntos no sean colineales o estén mal ingresados.")
        else:
            st.session_state["splines_q"] = splines
            st.session_state["x_q"] = x_ord
            st.session_state["y_q"] = y_ord
if "splines_q" in st.session_state:
    splines = st.session_state["splines_q"]
    x_g = st.session_state["x_q"]
    y_g = st.session_state["y_q"]

    st.subheader("Polinomios por tramo")
    for i, (a, b, c, xi, xi1) in enumerate(splines):
        p = np.poly1d([a, b - 2*a*xi, a*xi**2 - b*xi + c])
        coef_a = round(p[2], 4)
        coef_b = round(p[1], 4)
        coef_c = round(p[0], 4)
        signo_b = "+" if coef_b >= 0 else "-"
        signo_c = "+" if coef_c >= 0 else "-"
        st.code(f"S{i}(x) = {coef_a}x²  {signo_b}  {abs(coef_b)}x  {signo_c}  {abs(coef_c)},   x ∈ [{xi}, {xi1}]")

    st.subheader("Tabla de coeficientes")
    filas = [{"Tramo": f"S{i}", "x_i": xi, "x_i+1": xi1,
              "a (cuadrático)": round(a, 6), "b (lineal)": round(b, 6), "c (independiente)": round(c, 6)}
             for i, (a, b, c, xi, xi1) in enumerate(splines)]
    st.dataframe(pd.DataFrame(filas), use_container_width=True)

    st.subheader("Evaluar el spline")
    xp = st.number_input("Valor a interpolar (x)", key=f"xp_{st.session_state['reset']}")
    if st.button("Evaluar"):
        resultado = evaluar_spline(splines, xp)
        if resultado is None:
            st.error(f"⚠️ xₚ = {xp} está fuera del rango [{x_g[0]}, {x_g[-1]}].")
        else:
            st.success(f"S({xp}) = {resultado:.6f}")

            x_vals = np.linspace(min(x_g), max(x_g), 300)
            y_vals = [evaluar_spline(splines, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label="Spline Cuadrática")
            ax.scatter(x_g, y_g, zorder=5, label="Puntos dados")
            ax.scatter(xp, resultado, color="red", zorder=6, label=f"S({xp}) = {resultado:.4f}")
            ax.set_title("Spline Cuadrática")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.legend()
            st.pyplot(fig)

    st.divider()
    if st.button("Limpiar"):
        reset_val = st.session_state["reset"] + 1
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["reset"] = reset_val
        st.rerun()