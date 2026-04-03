import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
st.set_page_config(page_title="Polinomio de Hermite", page_icon="images/Logo.ico", layout="centered")

st.title("Interpolación por polinomio de Hermite")
st.write("Ingrese los puntos (valor de la función y su derivada):")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0

x = []
y = []
dy = []

modo = st.selectbox("Modo de ingreso", ["Manual", "Cargar desde Excel"], index=None)

if modo == "Cargar desde Excel":
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"], key=f"file_uploader_{st.session_state['reset']}")
    st.caption("El archivo debe tener columnas nombradas: x, y, dy")
    if archivo:
        df = pd.read_excel(archivo)
        x  = df["x"].tolist()
        y  = df["y"].tolist()
        dy = df["dy"].tolist()
        n  = len(x)
        st.success(f"{n} puntos cargados correctamente")
        st.dataframe(df, use_container_width=True)
if modo == "Manual" :
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=2))
    for i in range(n):
        st.markdown(f"**Punto {i}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            xi = st.number_input(f"x{i}", key=f"x{i}_{st.session_state['reset']}", value=0.0)
        with col2:
            yi = st.number_input(f"f(x{i})", key=f"y{i}_{st.session_state['reset']}", value=0.0)
        with col3:
            dyi = st.number_input(f"f'(x{i})", key=f"dy{i}_{st.session_state['reset']}", value=0.0)
        x.append(float(xi))
        y.append(float(yi))
        dy.append(float(dyi))


def tabla_hermite(x, y, dy):
    n = len(x)
    m = 2 * n
    z = np.zeros(m)
    Q = np.zeros((m, m))
    for i in range(n):
        z[2*i]        = x[i]
        z[2*i + 1]    = x[i]
        Q[2*i][0]     = y[i]
        Q[2*i + 1][0] = y[i]
        Q[2*i + 1][1] = dy[i]
        if i > 0:
            Q[2*i][1] = (Q[2*i][0] - Q[2*i - 1][0]) / (z[2*i] - z[2*i - 1])
    for j in range(2, m):
        for i in range(j, m):
            Q[i][j] = (Q[i][j-1] - Q[i-1][j-1]) / (z[i] - z[i-j])
    return z, Q


def evaluar_hermite(z, Q, xp):
    m = len(z)
    coefs = [Q[i][i] for i in range(m)]
    resultado = coefs[0]
    producto = 1
    for i in range(1, m):
        producto *= (xp - z[i-1])
        resultado += coefs[i] * producto
    return resultado


def formato_polinomio(z, Q, n_puntos):
    m = 2 * n_puntos
    coefs = [Q[i][i] for i in range(m)]
    terminos = []
    for i in range(m):
        c = round(coefs[i], 4)
        if abs(c) < 1e-10:
            continue
        signo = "+" if c > 0 and terminos else ""
        if i == 0:
            terminos.append(f"{c}")
        elif i == 1:
            terminos.append(f"{signo}{c}(x - {round(z[0], 4)})")
        else:
            producto = "".join([f"(x - {round(z[k], 4)})" for k in range(i)])
            terminos.append(f"{signo}{c}{producto}")
    return "H(x) = " + " ".join(terminos) if terminos else "H(x) = 0"


def construir_tabla_df(z, Q):
    m = len(z)
    col_names = ["i", "zᵢ", "f[zᵢ]"]
    for orden in range(1, m):
        if orden == 1:
            col_names.append("f[zᵢ, zᵢ₊₁]")
        elif orden == 2:
            col_names.append("f[zᵢ, zᵢ₊₁, zᵢ₊₂]")
        else:
            col_names.append(f"Orden {orden}")
    filas = []
    for i in range(m):
        fila = [i, round(z[i], 4), round(Q[i][0], 6)]
        for j in range(1, m):
            if j <= i:
                fila.append(round(Q[i][j], 6))
            else:
                fila.append("")
        filas.append(fila)
    return pd.DataFrame(filas, columns=col_names)


if st.button("Calcular"):
    # --- Validación: datos vacíos ---
    if len(x) == 0:
        st.error("⚠️ No hay datos ingresados")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        z, Q = tabla_hermite(x, y, dy)
        st.session_state["z"] = z
        st.session_state["Q"] = Q
        st.session_state["x"] = x
        st.session_state["y"] = y
        st.session_state["n_puntos"] = len(x)

if "z" in st.session_state:
    z   = st.session_state["z"]
    Q   = st.session_state["Q"]
    x_g = st.session_state["x"]
    y_g = st.session_state["y"]
    n_p = st.session_state["n_puntos"]

    st.subheader("Tabla de diferencias divididas (nodos duplicados)")
    st.caption("Los pares de filas con el mismo zᵢ corresponden al nodo duplicado de cada punto. "
               "La celda f[zᵢ, zᵢ₊₁] del nodo duplicado es la derivada ingresada.")
    df = construir_tabla_df(z, Q)
    st.dataframe(df, use_container_width=True)

    st.subheader("Polinomio de Hermite H(x)")
    st.code(formato_polinomio(z, Q, n_p))

    st.subheader("Polinomio derivado H'(x)")
    m = 2 * n_p
    coefs_h = [Q[i][i] for i in range(m)]
    poly = np.poly1d([coefs_h[0]])
    prod = np.poly1d([1.0])
    for i in range(1, m):
        prod = prod * np.poly1d([1, -z[i-1]])
        poly = poly + np.poly1d([coefs_h[i]]) * prod
    deriv = poly.deriv()
    grado = deriv.order
    terminos_d = []
    for exp in range(grado, -1, -1):
        c_r = round(deriv.coef[grado - exp], 4)
        if abs(c_r) < 1e-10:
            continue
        signo = "+" if c_r > 0 and terminos_d else ""
        if exp == 0:
            terminos_d.append(f"{signo}{c_r}")
        elif exp == 1:
            terminos_d.append(f"{signo}{c_r}x")
        else:
            terminos_d.append(f"{signo}{c_r}x^{exp}")
    polinomio_deriv = "H'(x) = " + " ".join(terminos_d) if terminos_d else "H'(x) = 0"
    st.code(polinomio_deriv)

    # --- Evaluación con validación de rango ---
    st.subheader("Evaluar el polinomio")
    x_min = min(x_g)
    x_max = max(x_g)
    st.caption(f"Rango válido de interpolación: [{x_min}, {x_max}]")
    xp = st.number_input("Valor a interpolar (x)")

    if st.button("Evaluar"):
        if xp < x_min or xp > x_max:
            st.error(f"⚠️ x = {xp} está fuera del rango [{x_min}, {x_max}]. ")
        else:
            resultado = evaluar_hermite(z, Q, xp)
            st.success(f"H({xp}) = {resultado}")

            x_vals = np.linspace(x_min, x_max, 200)
            y_vals = [evaluar_hermite(z, Q, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.scatter(x_g, y_g)
            ax.scatter(xp, resultado)
            ax.set_title("Polinomio de Interpolación (Hermite)")
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