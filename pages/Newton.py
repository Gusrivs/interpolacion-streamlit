import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
st.set_page_config(page_title="Newton", page_icon="images/Logo.ico", layout="centered")

st.title("Interpolación de Newton")
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
    if len(x) == 0:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        tabla = diferencias_divididas(x, y)
        coefs = tabla[0, :]
        st.session_state["coefs"] = coefs
        st.session_state["tabla"] = tabla
        st.session_state["x"] = x
        st.session_state["y"] = y

if "coefs" in st.session_state:
    coefs = st.session_state["coefs"]
    tabla = st.session_state["tabla"]
    x_g   = st.session_state["x"]
    y_g   = st.session_state["y"]
    n     = len(x_g)

    st.subheader("Polinomio de Newton")
    st.code(formato_polinomio(x_g, coefs))

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

    x_min = min(x_g)
    x_max = max(x_g)

    st.subheader("Evaluar el polinomio")
    st.caption(f"Rango con mayor precisión de interpolación: [{x_min}, {x_max}]")
    xp = st.number_input("Valor a interpolar (x)")

    if st.button("Evaluar"):
            resultado = evaluar_newton(x_g, coefs, xp)
            st.success(f"P({xp}) = {resultado}")

            x_vals = np.linspace(x_min, x_max, 100)
            y_vals = [evaluar_newton(x_g, coefs, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.scatter(x_g, y_g)
            ax.scatter(xp, resultado)
            ax.set_title("Polinomio de Interpolación (Newton)")
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