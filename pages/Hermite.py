import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import sympy as sp
from Utilidades.funcion import entrada_hermite_con_teclado, error_relativo

st.set_page_config(page_title="Polinomio de Hermite", page_icon="images/Logo.ico", layout="centered")

LOCALS_SYM = {
    "pi": sp.pi, "e": sp.E, "sqrt": sp.sqrt,
    "ln": sp.log, "sin": sp.sin, "cos": sp.cos,
    "tan": sp.tan, "exp": sp.exp,
}

def parsear_valor(texto: str):
    try:
        val = float(sp.sympify(texto.strip(), locals=LOCALS_SYM).evalf())
        return val, None
    except Exception:
        return None, f"No se pudo interpretar '{texto}'"

def teclado_simbolos():
    with st.expander("🔣 Símbolos disponibles para los inputs"):
        st.caption("Podés escribir estos símbolos directamente en cualquier campo:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.code("pi")
            st.code("e")
            st.code("^")
        with col2:
            st.code("sqrt(x)")
            st.code("ln(x)")
        with col3:
            st.code("sin(x)")
            st.code("cos(x)")
        with col4:
            st.code("1/3")
            st.code("-pi/2")
        st.caption("Ejemplos: `pi/2`, `sqrt(2)`, `e`, `ln(2)`, `1/3`, `-pi`")

st.title("Interpolación por polinomio de Hermite")
st.write("Ingrese los puntos (valor de la función y su derivada):")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0

x = []
y = []
derivadas = {}
parse_errors = []
f_original = None

modo = st.selectbox("Modo de ingreso", ["Manual", "Cargar desde Excel", "Función"], index=None)

# ── EXCEL ──────────────────────────────────────────────────────────────────────
if modo == "Cargar desde Excel":
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"],
                                key=f"file_uploader_{st.session_state['reset']}")
    st.caption("Columnas requeridas: x, y | Opcionales: dy1, dy2, dy3... (dejar vacío si no aplica)")
    if archivo:
        df = pd.read_excel(archivo)
        x = df["x"].tolist()
        y = df["y"].tolist()
        col_derivadas = sorted(
            [c for c in df.columns if c.startswith("dy") and c[2:].isdigit()],
            key=lambda c: int(c[2:])
        )
        for i in range(len(x)):
            derivadas[i] = {}
            for col in col_derivadas:
                orden = int(col[2:])
                val = df[col].iloc[i]
                if not pd.isna(val):
                    derivadas[i][orden] = float(val)
        n = len(x)
        st.success(f"{n} puntos cargados — derivadas detectadas: {col_derivadas if col_derivadas else 'ninguna'}")
        st.dataframe(df, use_container_width=True)

# ── MANUAL ─────────────────────────────────────────────────────────────────────
if modo == "Manual":
    teclado_simbolos()
    n  = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=2,
                              key=f"n_{st.session_state['reset']}"))
    nd = int(st.number_input("Orden máximo de derivada disponible", min_value=1, step=1, value=1,
                              key=f"nd_{st.session_state['reset']}"))

    for i in range(n):
        st.markdown(f"**Punto {i}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            xi_str = st.text_input(f"x{i}", value="0", placeholder="ej: pi/2, sqrt(2)",
                                    key=f"x{i}_{st.session_state['reset']}")
        with col2:
            yi_str = st.text_input(f"f(x{i})", value="0", placeholder="ej: e, ln(2)",
                                    key=f"y{i}_{st.session_state['reset']}")

        xi, err_x = parsear_valor(xi_str)
        yi, err_y = parsear_valor(yi_str)
        if err_x: parse_errors.append(f"Punto {i} x: {err_x}")
        if err_y: parse_errors.append(f"Punto {i} y: {err_y}")
        if xi is not None: x.append(xi)
        if yi is not None: y.append(yi)
        derivadas[i] = {}

        for d in range(1, nd + 1):
            with col3:
                col_check, col_val = st.columns([1, 2])
                with col_check:
                    tiene = st.checkbox(f"f^({d})", key=f"check_{i}_{d}_{st.session_state['reset']}")
                with col_val:
                    if tiene:
                        val_str = st.text_input(f"f^({d})(x{i})", value="0",
                                                 placeholder="ej: 1, -pi",
                                                 key=f"dy_{i}_{d}_{st.session_state['reset']}")
                        val, err_d = parsear_valor(val_str)
                        if err_d:
                            parse_errors.append(f"Punto {i} f^({d}): {err_d}")
                        else:
                            derivadas[i][d] = val

    for err in parse_errors:
        st.warning(f"⚠️ {err}")

# ── FUNCIÓN ────────────────────────────────────────────────────────────────────
if modo == "Función":
    datos = entrada_hermite_con_teclado(key_prefix="hermite")
    if datos["valida"]:
        x          = datos["x_vals"]
        y          = datos["y_vals"]
        derivadas  = datos["derivadas"]
        f_original = datos["f"]
    else:
        x, y, derivadas = [], [], {}


# ── FUNCIONES DE CÁLCULO ───────────────────────────────────────────────────────
def tabla_hermite(x, y, derivadas):
    z = []
    f_z = []
    for i in range(len(x)):
        num_repeticiones = len(derivadas.get(i, {})) + 1
        for _ in range(num_repeticiones):
            z.append(x[i])
            f_z.append(y[i])

    z = np.array(z)
    m = len(z)
    Q = np.zeros((m, m))
    Q[:, 0] = f_z

    for j in range(1, m):
        for i in range(m - 1, j - 1, -1):
            if z[i] == z[i - j]:
                idx_original = list(x).index(z[i])
                valor_derivada = derivadas.get(idx_original, {}).get(j, 0.0)
                Q[i][j] = valor_derivada / math.factorial(j)
            else:
                Q[i][j] = (Q[i][j - 1] - Q[i - 1][j - 1]) / (z[i] - z[i - j])

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


def formato_polinomio(z, Q, cifras=6):
    m = len(z)
    coefs = [Q[i][i] for i in range(m)]
    terminos = []
    for i in range(m):
        c = float(f"{coefs[i]:.{cifras}g}")
        if abs(c) < 1e-10:
            continue
        signo = "+" if c > 0 and terminos else ""
        if i == 0:
            terminos.append(f"{c}")
        elif i == 1:
            terminos.append(f"{signo}{c}(x - {round(z[0], cifras)})")
        else:
            producto = "".join([f"(x - {round(z[k], cifras)})" for k in range(i)])
            terminos.append(f"{signo}{c}{producto}")
    return "H(x) = " + " ".join(terminos) if terminos else "H(x) = 0"


def formato_polinomio_reducido(z, Q, cifras=6):
    m = len(z)
    coefs = [Q[i][i] for i in range(m)]
    p_final = np.poly1d([0.0])
    p_acum  = np.poly1d([1.0])
    for i in range(m):
        if i == 0:
            p_final += np.poly1d([coefs[i]])
        else:
            p_acum  *= np.poly1d([1.0, -z[i-1]])
            p_final += coefs[i] * p_acum
    grado = p_final.order
    terminos = []
    for exp in range(grado, -1, -1):
        c = float(f"{p_final.coef[grado - exp]:.{cifras}g}")
        if abs(c) < 1e-10:
            continue
        signo = " + " if c > 0 and terminos else " - " if c < 0 and terminos else ""
        if not terminos and c < 0:
            signo = "-"
        val = abs(c)
        if exp == 0:
            terminos.append(f"{signo}{val}")
        elif exp == 1:
            terminos.append(f"{signo}{val}x" if val != 1 else f"{signo}x")
        else:
            terminos.append(f"{signo}{val}x^{exp}" if val != 1 else f"{signo}x^{exp}")
    return "H(x) = " + "".join(terminos) if terminos else "H(x) = 0"


def formato_derivada(z, Q, cifras=6):
    m = len(z)
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
        c_r = float(f"{deriv.coef[grado - exp]:.{cifras}g}")
        if abs(c_r) < 1e-10:
            continue
        signo = "+" if c_r > 0 and terminos_d else ""
        if exp == 0:
            terminos_d.append(f"{signo}{c_r}")
        elif exp == 1:
            terminos_d.append(f"{signo}{c_r}x")
        else:
            terminos_d.append(f"{signo}{c_r}x^{exp}")
    return "H'(x) = " + " ".join(terminos_d) if terminos_d else "H'(x) = 0"


def construir_tabla_df(z, Q):
    m = len(z)
    col_names = ["zᵢ", "f[zᵢ]"]
    for orden in range(1, m):
        if orden == 1:
            col_names.append("f[zᵢ, zᵢ₊₁]")
        elif orden == 2:
            col_names.append("f[zᵢ, zᵢ₊₁, zᵢ₊₂]")
        else:
            col_names.append(f"Orden {orden}")
    filas = []
    for i in range(m):
        fila = [round(z[i], 4), round(Q[i][0], 6)]
        for j in range(1, m):
            fila.append(round(Q[i][j], 6) if j <= i else "")
        filas.append(fila)
    return pd.DataFrame(filas, columns=col_names)


# ── BOTÓN CALCULAR ─────────────────────────────────────────────────────────────
if st.button("Calcular"):
    if parse_errors:
        st.error("⚠️ Corregí los errores en los inputs antes de calcular.")
    elif len(x) == 0:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("⚠️ Todos los puntos deben tener x distintos.")
    else:
        indices   = sorted(range(len(x)), key=lambda i: x[i])
        x         = [x[i] for i in indices]
        y         = [y[i] for i in indices]
        derivadas = {nuevo: derivadas[viejo] for nuevo, viejo in enumerate(indices)}
        z, Q = tabla_hermite(x, y, derivadas)
        st.session_state["z"]          = z
        st.session_state["Q"]          = Q
        st.session_state["x"]          = x
        st.session_state["y"]          = y
        st.session_state["f_original"] = f_original

# ── RESULTADOS ─────────────────────────────────────────────────────────────────
if "z" in st.session_state:
    z          = st.session_state["z"]
    Q          = st.session_state["Q"]
    x_g        = st.session_state["x"]
    y_g        = st.session_state["y"]
    f_original = st.session_state["f_original"]

    st.subheader("Tabla de diferencias divididas (nodos duplicados)")
    st.caption("Los pares de filas con el mismo zᵢ corresponden al nodo duplicado de cada punto.")
    st.dataframe(construir_tabla_df(z, Q), use_container_width=True)

    st.subheader("Polinomio de Hermite H(x) sin reducir")
    st.code(formato_polinomio(z, Q))

    st.subheader("Polinomio de Hermite H(x) reducido")
    st.code(formato_polinomio_reducido(z, Q))

    st.subheader("Polinomio derivado H'(x)")
    st.code(formato_derivada(z, Q))

    x_min = min(x_g)
    x_max = max(x_g)

    st.subheader("Evaluar el polinomio")
    st.caption(f"Rango con mayor precisión de interpolación: [{x_min}, {x_max}]")
    if modo == "Manual":
        teclado_simbolos()
    xp_str = st.text_input("Valor a interpolar (x)", value="0",
                             placeholder="ej: pi/2, sqrt(2), 0.9",
                             key=f"xp_{st.session_state['reset']}")

    if st.button("Evaluar"):
        xp, err_xp = parsear_valor(xp_str)
        if err_xp:
            st.error(f"⚠️ {err_xp}")
        else:
            resultado = evaluar_hermite(z, Q, xp)
            st.success(f"H({xp_str}) = {resultado}")

            if f_original is not None:
                f_real = f_original(xp)
                if f_real is not None and f_real != 0:
                    err = error_relativo(f_real, resultado)
                    st.info(f"f({xp_str}) real = {f_real:.9f} | Error relativo: {err:.6f}%")

            x_min_g = min(x_min, xp)
            x_max_g = max(x_max, xp)
            x_vals  = np.linspace(x_min_g, x_max_g, 200)
            y_vals  = [evaluar_hermite(z, Q, xi) for xi in x_vals]

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