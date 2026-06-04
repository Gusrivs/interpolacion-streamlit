import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Spline Cúbico", page_icon="images/Logo.ico", layout="centered")
st.title("Interpolación por Spline Cúbico")
st.write("Ingrese los puntos para construir los splines cúbicos naturales:")

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


def spline_cubico_natural(x, y):
    n = len(x)
    m = n - 1
    h = [x[i + 1] - x[i] for i in range(m)]
    size = n - 2
    A = np.zeros((size, size))
    b_vec = np.zeros(size)
    for i in range(size):
        A[i][i] = 2 * (h[i] + h[i + 1])
        if i > 0:
            A[i][i - 1] = h[i]
        if i < size - 1:
            A[i][i + 1] = h[i + 1]
        b_vec[i] = 6 * ((y[i + 2] - y[i + 1]) / h[i + 1] - (y[i + 1] - y[i]) / h[i])
    try:
        M_interior = np.linalg.solve(A, b_vec) if size > 0 else np.array([])
    except np.linalg.LinAlgError:
        return None, None
    M = np.concatenate([[0], M_interior, [0]])
    splines = []
    for i in range(m):
        a = y[i]
        b = (y[i + 1] - y[i]) / h[i] - h[i] * (2 * M[i] + M[i + 1]) / 6
        c = M[i] / 2
        d = (M[i + 1] - M[i]) / (6 * h[i])
        splines.append((a, b, c, d, x[i], x[i + 1]))
    return splines, M


def evaluar_spline(splines, xp):
    for (a, b, c, d, xi, xi1) in splines:
        if xi <= xp <= xi1:
            t = xp - xi
            return a + b * t + c * t ** 2 + d * t ** 3
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
        splines, M = spline_cubico_natural(x_ord, y_ord)
        if splines is None:
            st.error("⚠️ El sistema no tiene solución. Verificá que los puntos no sean colineales o estén mal ingresados.")
        else:
            st.session_state["splines_c"] = splines
            st.session_state["M_c"] = M
            st.session_state["x_c"] = x_ord
            st.session_state["y_c"] = y_ord

if "splines_c" in st.session_state:
    splines = st.session_state["splines_c"]
    M = st.session_state["M_c"]
    x_g = st.session_state["x_c"]
    y_g = st.session_state["y_c"]

    st.subheader("Momentos (segundas derivadas en los nodos)")
    st.caption("Condición de spline natural: M₀ = 0 y Mₙ = 0")
    filas_m = [{"i": i, "xᵢ": round(x_g[i], 4), "Mᵢ (Segunda derivada)": round(M[i], 6)}
               for i in range(len(x_g))]
    st.dataframe(pd.DataFrame(filas_m), use_container_width=True)

    st.subheader("Polinomios por tramo")
    for i, (a, b, c, d, xi, xi1) in enumerate(splines):
        signo_b = "+" if b >= 0 else "-"
        signo_c = "+" if c >= 0 else "-"
        signo_d = "+" if d >= 0 else "-"
        st.code(
            f"S{i}(x) = {round(a,4)}  {signo_b}  {abs(round(b,4))}·(x - {xi})"
            f"  {signo_c}  {abs(round(c,4))}·(x - {xi})²"
            f"  {signo_d}  {abs(round(d,4))}·(x - {xi})³,   x ∈ [{xi}, {xi1}]"
        )

    st.subheader("Tabla de coeficientes")
    filas = [{"Tramo": f"S{i}", "x_i": xi, "x_i+1": xi1,
              "a": round(a, 6), "b": round(b, 6), "c": round(c, 6), "d": round(d, 6)}
             for i, (a, b, c, d, xi, xi1) in enumerate(splines)]
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
            ax.plot(x_vals, y_vals, label="Spline Cúbico Natural")
            ax.scatter(x_g, y_g, zorder=5, label="Puntos dados")
            ax.scatter(xp, resultado, color="red", zorder=6, label=f"S({xp}) = {resultado:.4f}")
            ax.set_title("Spline Cúbico Natural")
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