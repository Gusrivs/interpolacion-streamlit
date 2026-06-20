import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Spline Grado Cero", page_icon="images/Logo.ico", layout="centered")
st.title("Interpolación por Spline de Grado Cero")
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
        df = df.sort_values("x").reset_index(drop=True)
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


def spline_grado_cero(x, y):
    tramos = []
    for i in range(len(x) - 1):
        tramos.append((x[i], x[i + 1], y[i]))
    return tramos


def evaluar_spline(tramos, xp, y_ultimo):
    for (x0, x1, a) in tramos:
        if x0 <= xp < x1:
            return a
    # Si xp es exactamente el último punto, usar el último y ingresado
    if xp == tramos[-1][1]:
        return y_ultimo
    return None


if st.button("Calcular"):
    if len(x) < 2:
        st.error("⚠️ Se necesitan al menos 2 puntos.")
    elif len(set(x)) != len(x):
        st.error("⚠️ Todos los puntos deben tener x distintos.")
    else:
        pares = sorted(zip(x, y), key=lambda p: p[0])
        x_ord = [p[0] for p in pares]
        y_ord = [p[1] for p in pares]
        tramos = spline_grado_cero(x_ord, y_ord)
        st.session_state["tramos_0"] = tramos
        st.session_state["x_0"] = x_ord
        st.session_state["y_0"] = y_ord

if "tramos_0" in st.session_state:
    tramos = st.session_state["tramos_0"]
    x_g = st.session_state["x_0"]
    y_g = st.session_state["y_0"]

    st.subheader("Polinomios por tramo")
    for i, (x0, x1, a) in enumerate(tramos):
        st.code(f"S{i}(x) = {a},   x ∈ [{x0}, {x1})")

    st.subheader("Tabla de coeficientes")
    filas = [{"Tramo": f"S{i}", "x_i": x0, "x_i+1": x1, "a (constante)": a}
             for i, (x0, x1, a) in enumerate(tramos)]
    st.dataframe(pd.DataFrame(filas), use_container_width=True)

    st.subheader("Evaluar el spline")
    xp = st.number_input("Valor a interpolar (x)", key=f"xp_{st.session_state['reset']}")
    if st.button("Evaluar"):
        resultado = evaluar_spline(tramos, xp, y_g[-1])
        if resultado is None:
            st.error(f"⚠️ xₚ = {xp} está fuera del rango [{x_g[0]}, {x_g[-1]}].")
        else:
            st.success(f"S({xp}) = {resultado:.6f}")

            # Gráfica escalonada
            x_vals = []
            y_vals = []
            for (x0, x1, a) in tramos:
                x_vals += [x0, x1]
                y_vals += [a, a]

            fig, ax = plt.subplots()
            ax.step(x_g, y_g, where="post", label="Spline Grado Cero", linewidth=2)
            ax.scatter(x_g, y_g, zorder=5, label="Puntos dados")
            ax.scatter(xp, resultado, color="red", zorder=6, label=f"S({xp}) = {resultado:.4f}")
            ax.set_title("Spline de Grado Cero")
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