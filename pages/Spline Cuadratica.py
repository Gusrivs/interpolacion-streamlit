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


def spline_cuadratica(x, y):
    n = len(x)
    m = n - 1  # número de intervalos
    # Cada spline cuadrático tiene 3 coeficientes: a, b, c → 3m incógnitas
    # Condiciones:
    # 1) S_i(x_i) = y_i  → m ecuaciones
    # 2) S_i(x_{i+1}) = y_{i+1} → m ecuaciones
    # 3) Continuidad de primera derivada en nodos interiores → m-1 ecuaciones
    # 4) Condición de frontera libre: a_0 = 0 (primer coeficiente cuadrático = 0)
    # Total: m + m + (m-1) + 1 = 3m ecuaciones ✓

    size = 3 * m
    A = np.zeros((size, size))
    b_vec = np.zeros(size)

    eq = 0
    for i in range(m):
        # S_i(x_i) = y_i
        hi = x[i + 1] - x[i]
        # S_i(t) = a_i*(t-x_i)^2 + b_i*(t-x_i) + c_i
        # S_i(x_i) = c_i = y_i
        A[eq][3 * i + 2] = 1
        b_vec[eq] = y[i]
        eq += 1

        # S_i(x_{i+1}) = y_{i+1}
        A[eq][3 * i]     = hi ** 2
        A[eq][3 * i + 1] = hi
        A[eq][3 * i + 2] = 1
        b_vec[eq] = y[i + 1]
        eq += 1

    # Continuidad de primera derivada en nodos interiores
    # S_i'(x_{i+1}) = S_{i+1}'(x_{i+1})
    # 2*a_i*h_i + b_i = b_{i+1}
    for i in range(m - 1):
        hi = x[i + 1] - x[i]
        A[eq][3 * i]     =  2 * hi
        A[eq][3 * i + 1] =  1
        A[eq][3 * i + 4] = -1  # b_{i+1}
        b_vec[eq] = 0
        eq += 1

    # Condición de frontera: a_0 = 0
    A[eq][0] = 1
    b_vec[eq] = 0

    coefs = np.linalg.solve(A, b_vec)
    # Reorganizar coeficientes por tramo
    splines = []
    for i in range(m):
        a = coefs[3 * i]
        b = coefs[3 * i + 1]
        c = coefs[3 * i + 2]
        splines.append((a, b, c, x[i], x[i + 1]))
    return splines


def evaluar_spline(splines, xp):
    for (a, b, c, xi, xi1) in splines:
        if min(xi, xi1) <= xp <= max(xi, xi1):
            t = xp - xi
            return a * t ** 2 + b * t + c
    return None


def construir_tabla_df(splines, x):
    filas = []
    for i, (a, b, c, xi, xi1) in enumerate(splines):
        filas.append({
            "Tramo": f"[{round(xi, 4)}, {round(xi1, 4)}]",
            "a (cuadrático)": round(a, 6),
            "b (lineal)": round(b, 6),
            "c (independiente)": round(c, 6),
            "Polinomio S(x)": f"{round(a,4)}(x-{round(xi,4)})² + {round(b,4)}(x-{round(xi,4)}) + {round(c,4)}"
        })
    return pd.DataFrame(filas)


if st.button("Calcular"):
    if len(x) < 3:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        splines = spline_cuadratica(x, y)
        st.session_state["splines_q"] = splines
        st.session_state["x_q"] = x
        st.session_state["y_q"] = y

if "splines_q" in st.session_state:
    splines = st.session_state["splines_q"]
    x_g = st.session_state["x_q"]
    y_g = st.session_state["y_q"]

    st.subheader("Coeficientes por tramo")
    st.caption("Cada spline tiene la forma: S(x) = a(x - xᵢ)² + b(x - xᵢ) + c")
    df = construir_tabla_df(splines, x_g)
    st.dataframe(df, use_container_width=True)

    st.subheader("Evaluar el spline")
    xp = st.number_input("Valor a interpolar (x)")

    if st.button("Evaluar"):
        resultado = evaluar_spline(splines, xp)
        if resultado is not None:
            st.success(f"S({xp}) = {resultado}")

            x_vals = np.linspace(min(x_g), max(x_g), 300)
            y_vals = [evaluar_spline(splines, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals, label="Spline Cuadrática")
            ax.scatter(x_g, y_g, color="red", zorder=5, label="Puntos datos")
            ax.scatter(xp, resultado, color="green", zorder=6, label=f"S({xp})={round(resultado,4)}")
            ax.set_title("Spline Cuadrática")
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.legend()
            st.pyplot(fig)
        else:
            st.error(f"El valor x={xp} está fuera del rango de interpolación [{min(x_g)}, {max(x_g)}].")

    st.divider()
    if st.button("Limpiar"):
        reset_val = st.session_state["reset"] + 1
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["reset"] = reset_val
        st.rerun()