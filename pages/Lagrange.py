import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.title("Interpolación de Lagrange")
st.write("Ingrese los puntos:")

x = []
y = []
entrada = st.selectbox("Como desea agregar los datos?", ("Manualmente", "Importar xlsx, xls"), index=None)
if (entrada == "Manualmente"):
    st.write("Ingrese:")
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=2))
    for i in range(n):
        col1, col2 = st.columns(2)
        with col1:
            xi = st.number_input(f"x{i}", key=f"x{i}")
        with col2:
            yi = st.number_input(f"y{i}", key=f"y{i}")
        x.append(float(xi))
        y.append(float(yi))
if (entrada == "Importar xlsx, xls"):
    archivo = st.file_uploader("Cargar puntos desde Excel", type=["xlsx", "xls"])
    st.success("El archivo debe contener una tabla de dos columnas con encabezados x, y respectivamente")
    if archivo:
        df = pd.read_excel(archivo)
        x = df["x"].tolist()
        y = df["y"].tolist()
        n = len(x)
        st.success(f"{n} puntos cargados correctamente")
        st.dataframe(df, use_container_width=True)

def lagrange_coeficientes(x, y):
    return np.polyfit(x, y, len(x) - 1)

def formato_polinomio(coefs):
    grado = len(coefs) - 1
    terminos = []
    for i, c in enumerate(coefs):
        exp = grado - i
        c_r = round(c, 4)
        if abs(c_r) < 1e-10:
            continue
        signo = "+" if c_r > 0 and terminos else ""
        if exp == 0:
            terminos.append(f"{signo}{c_r}")
        elif exp == 1:
            terminos.append(f"{signo}{c_r}x")
        else:
            terminos.append(f"{signo}{c_r}x^{exp}")
    return "P(x) = " + " ".join(terminos) if terminos else "P(x) = 0"

if st.button("Construir polinomio"):
    coefs = lagrange_coeficientes(x, y)
    st.session_state["coefs"] = coefs
    st.session_state["x"] = x
    st.session_state["y"] = y

if "coefs" in st.session_state:
    coefs = st.session_state["coefs"]
    x_guardado = st.session_state["x"]
    y_guardado = st.session_state["y"]

    st.subheader("Polinomio de colocación")
    st.code(formato_polinomio(coefs))

    x_vals = np.linspace(min(x_guardado), max(x_guardado), 100)
    y_vals = np.polyval(coefs, x_vals)

    st.subheader("Evaluar el polinomio")
    xp = st.number_input("Valor a interpolar (x)")
    if st.button("Evaluar"):
        resultado = np.polyval(coefs, xp)
        st.success(f"P({xp}) = {resultado}")

        fig, ax = plt.subplots()
        ax.plot(x_vals, y_vals)
        ax.scatter(x_guardado, y_guardado)
        ax.scatter(xp, resultado)
        ax.set_title("Polinomio de Interpolación (Lagrange)")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        st.pyplot(fig)