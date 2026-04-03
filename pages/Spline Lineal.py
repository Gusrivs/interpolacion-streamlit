import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
st.set_page_config(page_title="Spline Lineal", page_icon="images/Logo.ico", layout="centered")
st.title("Interpolación por Spline Lineal")
st.write("Ingrese los puntos:")

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
        x = df["x"].tolist()
        y = df["y"].tolist()
        n = len(x)
        st.success(f"{n} puntos cargados correctamente")
        st.dataframe(df, use_container_width=True)

if modo == "Manual":
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=3,
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

def calcular_splines(x, y):
    tramos = []
    for i in range(len(x) - 1):
        a = y[i]
        b = (y[i+1] - y[i]) / (x[i+1] - x[i])
        tramos.append((x[i], x[i+1], a, b))
    return tramos

def evaluar_spline(tramos, xp):
    for (x0, x1, a, b) in tramos:
        if min(x0, x1) <= xp <= max(x0, x1):
            return a + b * (xp - x0)
    return None

if st.button("Calcular"):
    if len(x) < 3:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        tramos = calcular_splines(x, y)
        st.session_state["tramos"] = tramos
        st.session_state["x"] = x
        st.session_state["y"] = y

if "tramos" in st.session_state:
    tramos = st.session_state["tramos"]
    x_g = st.session_state["x"]
    y_g = st.session_state["y"]

    st.subheader("Polinomios por tramo")
    for i, (x0, x1, a, b) in enumerate(tramos):
        signo = "+" if b >= 0 else "-"
        st.code(f"S{i}(x) = {a} {signo} {abs(b):.4f}·(x - {x0}),   x ∈ [{x0}, {x1}]")

    st.subheader("Tabla de coeficientes")
    filas = [{"Tramo": f"S{i}", "x_i": x0, "x_i+1": x1, "a": a, "b": round(b, 6)}
             for i, (x0, x1, a, b) in enumerate(tramos)]
    st.dataframe(pd.DataFrame(filas), use_container_width=True)

    st.subheader("Evaluar el spline")
    xp = st.number_input("Valor a interpolar (x)", key=f"xp_{st.session_state['reset']}")
    if st.button("Evaluar"):
        resultado = evaluar_spline(tramos, xp)
        if resultado is None:
            if x_g[0] < x_g[-1]:
                st.error(f"xₚ = {xp} está fuera del rango [{x_g[0]}, {x_g[-1]}].")
            else:
                st.error(f"xₚ = {xp} está fuera del rango [{x_g[-1]}, {x_g[0]}].")
        else:
            st.success(f"S({xp}) = {resultado:.6f}")

            x_vals = np.linspace(min(x_g), max(x_g), 300)
            y_vals = [evaluar_spline(tramos, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label="Spline lineal")
            ax.scatter(x_g, y_g, zorder=5, label="Puntos dados")
            ax.scatter(xp, resultado, color="red", zorder=6, label=f"S({xp}) = {resultado:.4f}")
            ax.set_title("Spline Lineal")
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