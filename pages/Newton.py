import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sympy as sp

st.set_page_config(page_title="Newton", page_icon="images/Logo.ico", layout="centered")

LOCALS_SYM = {
    "pi": sp.pi, "e": sp.E, "sqrt": sp.sqrt,
    "ln": sp.log, "sin": sp.sin, "cos": sp.cos,
    "tan": sp.tan, "exp": sp.exp,
}

def parsear_valor(texto: str):
    """Convierte texto con símbolos a float. Retorna (float, None) o (None, error)."""
    try:
        val = float(sp.sympify(texto.strip(), locals=LOCALS_SYM).evalf())
        return val, None
    except Exception:
        return None, f"No se pudo interpretar '{texto}'"

def teclado_simbolos():
    """Mini teclado de referencia con símbolos copiables."""
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

st.title("Interpolación de Newton")
st.write("Ingrese los puntos:")

if "reset" not in st.session_state:
    st.session_state["reset"] = 0

x_raw = []
y_raw = []
x = []
y = []
parse_errors = []
f_original = None

modo = st.selectbox("Modo de ingreso", ["Manual", "Cargar desde Excel", "Función"], index=None)

if modo == "Cargar desde Excel":
    archivo = st.file_uploader("Subir archivo Excel", type=["xlsx", "xls"],
                                key=f"file_uploader_{st.session_state['reset']}")
    st.caption("El archivo debe tener columnas nombradas: x, y")
    if archivo:
        df = pd.read_excel(archivo)
        x = df["x"].tolist()
        y = df["y"].tolist()
        n = len(x)
        st.success(f"{n} puntos cargados correctamente")
        st.dataframe(df, use_container_width=True)

if modo == "Manual":
    teclado_simbolos()
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=3,
                             key=f"n_{st.session_state['reset']}"))
    for i in range(n):
        st.markdown(f"**Punto {i}**")
        col1, col2 = st.columns(2)
        with col1:
            xi_str = st.text_input(f"x{i}", value="0", placeholder="ej: pi/2, sqrt(2), 1/3",
                                    key=f"x{i}_{st.session_state['reset']}")
        with col2:
            yi_str = st.text_input(f"y{i}", value="0", placeholder="ej: e, ln(2), -1",
                                    key=f"y{i}_{st.session_state['reset']}")

        xi, err_x = parsear_valor(xi_str)
        yi, err_y = parsear_valor(yi_str)

        if err_x:
            parse_errors.append(f"Punto {i} — x: {err_x}")
        if err_y:
            parse_errors.append(f"Punto {i} — y: {err_y}")

        if xi is not None and yi is not None:
            x.append(xi)
            y.append(yi)
            x_raw.append(xi_str)
            y_raw.append(yi_str)

    for err in parse_errors:
        st.warning(f"⚠️ {err}")

if modo == "Función":
    try:
        from Utilidades.funcion import entrada_funcion_con_teclado, error_relativo as err_rel
        datos = entrada_funcion_con_teclado(key_prefix="newton")
        if datos["valida"]:
            x = datos["x_vals"]
            y = datos["y_vals"]
            f_original = datos["f"]
        else:
            x, y = [], []
    except ImportError:
        st.error("⚠️ Módulo Utilidades no encontrado.")


def diferencias_divididas(x, y):
    n = len(x)
    tabla = np.zeros((n, n))
    tabla[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            tabla[i][j] = (tabla[i+1][j-1] - tabla[i][j-1]) / (x[i+j] - x[i])
    return tabla


def evaluar_newton(x, coefs, xp):
    resultado = coefs[0]
    producto = 1
    for i in range(1, len(coefs)):
        producto *= (xp - x[i-1])
        resultado += coefs[i] * producto
    return resultado


def formato_polinomio_newton(x, coefs, cifras=6):
    terminos = []
    for i in range(len(coefs)):
        c = float(f"{coefs[i]:.{cifras}g}")
        if abs(c) < 1e-10:
            continue
        signo = "+" if c > 0 and terminos else ""
        if i == 0:
            terminos.append(f"{c}")
        elif i == 1:
            terminos.append(f"{signo}{c}(x - {round(x[0], cifras)})")
        else:
            producto = "".join([f"(x - {round(x[k], cifras)})" for k in range(i)])
            terminos.append(f"{signo}{c}{producto}")
    return "P(x) = " + " ".join(terminos) if terminos else "P(x) = 0"


def formato_polinomio_reducido(x, coefs, cifras=6):
    poly = np.poly1d([0.0])
    prod = np.poly1d([1.0])
    for i in range(len(coefs)):
        if i == 0:
            poly = poly + np.poly1d([coefs[i]])
        else:
            prod = prod * np.poly1d([1.0, -x[i-1]])
            poly = poly + np.poly1d([coefs[i]]) * prod
    grado = len(poly.coeffs) - 1
    terminos = []
    for i, c in enumerate(poly.coeffs):
        exp = grado - i
        c_r = float(f"{c:.{cifras}g}")
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


def construir_tabla_df(x_g, tabla):
    n = len(x_g)
    col_names = ["xᵢ", "f(xᵢ)"]
    for orden in range(1, n):
        nodos = ", ".join([f"x{k}" for k in range(orden + 1)])
        col_names.append(f"f({nodos})")

    display = [["" for _ in range(n)] for _ in range(n)]
    for j in range(n):
        vals_col = []
        for i in range(n):
            if i + j < n:
                vals_col.append(round(tabla[i][j], 6))
        start = n - len(vals_col)
        for k, v in enumerate(vals_col):
            display[start + k][j] = v

    filas = []
    for i in range(n):
        fila = [round(x_g[i], 6)] + display[i]
        filas.append(fila)
    return pd.DataFrame(filas, columns=col_names)


if st.button("Calcular"):
    if parse_errors:
        st.error("⚠️ Corregí los errores en los inputs antes de calcular.")
    elif len(x) == 0:
        st.error("⚠️ No hay datos ingresados.")
    elif len(set(x)) != len(x):
        st.error("⚠️ Todos los puntos deben tener x distintos.")
    else:
        tabla = diferencias_divididas(x, y)
        coefs = tabla[0, :]
        st.session_state["coefs"]      = coefs
        st.session_state["tabla"]      = tabla
        st.session_state["x"]          = x
        st.session_state["y"]          = y
        st.session_state["f_original"] = f_original

if "coefs" in st.session_state:
    coefs      = st.session_state["coefs"]
    tabla      = st.session_state["tabla"]
    x_g        = st.session_state["x"]
    y_g        = st.session_state["y"]
    f_original = st.session_state["f_original"]

    st.subheader("Tabla de diferencias divididas")
    df = construir_tabla_df(x_g, tabla)
    st.dataframe(df, use_container_width=True)

    st.subheader("Polinomio de Newton")
    st.caption("Forma Newton (sin reducir)")
    st.code(formato_polinomio_newton(x_g, coefs))
    st.caption("Forma estándar (reducida)")
    st.code(formato_polinomio_reducido(x_g, coefs))

    x_min = min(x_g)
    x_max = max(x_g)

    st.subheader("Evaluar el polinomio")
    st.caption(f"Rango con mayor precisión de interpolación: [{x_min}, {x_max}]")
    if modo == "Manual":
        teclado_simbolos()
    xp_str = st.text_input("Valor a interpolar (x)", value="0",
                             placeholder="ej: pi/2, sqrt(2), 1/3",
                             key=f"xp_{st.session_state['reset']}")

    if st.button("Evaluar"):
        xp, err_xp = parsear_valor(xp_str)
        if err_xp:
            st.error(f"⚠️ {err_xp}")
        else:
            resultado = evaluar_newton(x_g, coefs, xp)
            st.success(f"P({xp_str}) = {resultado}")

            if f_original is not None:
                f_real = f_original(xp)
                if f_real is not None and f_real != 0:
                    from Utilidades.funcion import error_relativo as err_rel
                    err = err_rel(f_real, resultado)
                    st.info(f"f({xp_str}) real = {f_real:.9f} | Error relativo: {err:.6f}%")

            x_min_g = min(x_min, xp)
            x_max_g = max(x_max, xp)
            x_vals = np.linspace(x_min_g, x_max_g, 200)
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