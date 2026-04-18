import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from Utilidades.funcion import entrada_funcion_con_teclado

st.set_page_config(page_title="Lagrange", page_icon="images/Logo.ico", layout="centered")

st.title("Interpolación de Lagrange")
st.write("Ingrese los puntos:")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0


x = []
y = []
coefs = None

modo = st.selectbox("Modo de ingreso", ["Manual", "Cargar desde Excel", "Función"], index=None)
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
if modo == "Función":
    datos = entrada_funcion_con_teclado(key_prefix="lagrange")
    if datos["valida"]:
        x = datos["x_vals"]
        y = datos["y_vals"]
    else:
        # Si no es válida, nos aseguramos de que x e y sean listas vacías
        x, y = [], []

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
    if len(x) == 0:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        coefs = lagrange_coeficientes(x, y)
        st.session_state["coefs"] = coefs
        st.session_state["x"] = x
        st.session_state["y"] = y

if "coefs" in st.session_state:
    coefs      = st.session_state["coefs"]
    x_guardado = st.session_state["x"]
    y_guardado = st.session_state["y"]

    st.subheader("Polinomio de colocación")
    st.code(formato_polinomio(coefs))

    x_min = min(x_guardado)
    x_max = max(x_guardado)
    x_vals = np.linspace(x_min, x_max, 100)
    y_vals = np.polyval(coefs, x_vals)

    st.subheader("Evaluar el polinomio")
    st.caption(f"Rango de interpolación con mayor grado de precisión: [{x_min}, {x_max}]")
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

    st.divider()
    if st.button("Limpiar"):
        reset_val = st.session_state["reset"] + 1
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["reset"] = reset_val
        st.rerun()