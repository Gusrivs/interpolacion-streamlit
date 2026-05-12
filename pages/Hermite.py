import streamlit as st
import numpy as np
import math
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
    if archivo:
        df = pd.read_excel(archivo)
        x = df["x"].tolist()
        y = df["y"].tolist()
        # Convertimos la columna 'dy' al formato de diccionario {i: {1: valor}}
        derivadas = {i: {1: row["dy"]} for i, row in df.iterrows() if not pd.isna(row["dy"])}
        n = len(x)
        st.success(f"{n} puntos cargados")
if modo == "Manual":
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=2, key=f"n_{st.session_state['reset']}"))
    nd = int(st.number_input("Orden máximo de derivada disponible", min_value=1, step=1, value=1,key=f"nd_{st.session_state['reset']}"))
    derivadas = {}  # dict: {i: {orden: valor}}

    for i in range(n):
        st.markdown(f"**Punto {i}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            xi = st.number_input(f"x{i}", key=f"x{i}_{st.session_state['reset']}", value=0.0, step=1e-2, format="%.9f", )
        with col2:
            yi = st.number_input(f"f(x{i})", key=f"y{i}_{st.session_state['reset']}", value=0.0, step=1e-2, format="%.9f")
        x.append(float(xi))
        y.append(float(yi))
        derivadas[i] = {}

        for d in range(1, nd + 1):
            with col3:
                col_check, col_val = st.columns([1, 2])
                with col_check:
                    tiene = st.checkbox(f"f^({d})",key=f"check_{i}_{d}_{st.session_state['reset']}")
                with col_val:
                    if tiene:
                        val = st.number_input(f"f^({d})", value=0.0, step=1e-2,format="%.9f", key=f"dy_{i}_{d}_{st.session_state['reset']}")
                        derivadas[i][d] = float(val)
        
def tabla_hermite(x, y, derivadas):
    """
    x: lista de puntos base
    y: lista de f(x)
    derivadas: dict {índice_punto: {orden: valor}}
    """
    # 1. Expandir los puntos z y la primera columna de Q
    z = []
    f_z = []
    
    for i in range(len(x)):
        # Repeticiones = 1 (la función) + número de derivadas disponibles para ese punto
        num_repeticiones = len(derivadas[i]) + 1
        for _ in range(num_repeticiones):
            z.append(x[i])
            f_z.append(y[i])
    
    z = np.array(z)
    m = len(z)
    Q = np.zeros((m, m))
    Q[:, 0] = f_z

    # 2. Llenar la tabla de diferencias divididas
    for j in range(1, m):
        for i in range(m - 1, j - 1, -1):
            
            # Caso: Nodos coincidentes (Usar la derivada proporcionada)
            if z[i] == z[i - j]:
                # Buscamos el índice original del punto x para saber sus derivadas
                # Usamos np.where para encontrar a qué índice de 'x' pertenece el valor z[i]
                idx_original = x.index(z[i])
                
                # El orden de la derivada corresponde a la columna 'j'
                valor_derivada = derivadas[idx_original].get(j, 0.0)
                
                # Formula: f[x_i, ..., x_i] = f^(j)(x_i) / j!
                Q[i][j] = valor_derivada / math.factorial(j)
            
            # Caso: Nodos distintos (Diferencia dividida estándar)
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


def formato_polinomio(z, Q):
    m = len(z) # Usar el largo real de z
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
    # Quitamos "i" de los nombres de columnas
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
        # Empezamos la fila directamente con z[i]
        fila = [round(z[i], 4), round(Q[i][0], 6)]
        for j in range(1, m):
            if j <= i:
                fila.append(round(Q[i][j], 6))
            else:
                fila.append("")
        filas.append(fila)
    return pd.DataFrame(filas, columns=col_names)

def formato_polinomio_reducido(z, Q):
    m = len(z)
    coefs = [Q[i][i] for i in range(m)]
    
    # Iniciamos el polinomio final en cero
    p_final = np.poly1d([0.0])
    # Termino acumulado de productos (x - z0)(x - z1)...
    p_acumulado = np.poly1d([1.0])
    for i in range(m):
        if i == 0:
            p_final += np.poly1d([coefs[i]])
        else:
            # Creamos el binomio (x - z_{i-1}) -> poly1d([1, -valor])
            binomio = np.poly1d([1.0, -z[i-1]])
            p_acumulado *= binomio
            p_final += coefs[i] * p_acumulado            
    # Formatear la salida de forma elegante
    grado = p_final.order
    terminos = []
    # Los coeficientes en poly1d van de mayor grado a menor
    for exp in range(grado, -1, -1):
        c = round(p_final.coef[grado - exp], 4)
        if abs(c) < 1e-10: continue 
        signo = " + " if c > 0 and terminos else " - " if c < 0 and terminos else ""
        if not terminos and c < 0: signo = "-" # Caso primer término negativo
        val = abs(c)
        if exp == 0:
            terminos.append(f"{signo}{val}")
        elif exp == 1:
            terminos.append(f"{signo}{val}x" if val != 1 else f"{signo}x")
        else:
            terminos.append(f"{signo}{val}x^{exp}" if val != 1 else f"{signo}x^{exp}")      
    return "H(x) = " + "".join(terminos) if terminos else "H(x) = 0"

def formato_polinomio_derivada(z, Q):
    st.subheader("Polinomio derivado H'(x)")
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
    return "H'(x) = " + " ".join(terminos_d) if terminos_d else "H'(x) = 0"

if st.button("Calcular"):
    if len(x) == 0:
        st.error("⚠️ No hay datos ingresados")
    elif len(set(x)) != len(x):
        st.error("Todos los puntos deben tener x distintos.")
    else:
        # IMPORTANTE: Pasar 'derivadas', no 'dy'
        z, Q = tabla_hermite(x, y, derivadas) 
        st.session_state["z"] = z
        st.session_state["Q"] = Q
        st.session_state["x"] = x
        st.session_state["y"] = y
        # El número total de filas en la tabla es len(z), no len(x)
        st.session_state["n_filas"] = len(z)

if "z" in st.session_state:
    z = st.session_state["z"]
    Q = st.session_state["Q"]
    n_filas = st.session_state["n_filas"]

    st.subheader("Tabla de diferencias divididas (nodos duplicados)")
    st.caption("Los pares de filas con el mismo zᵢ corresponden al nodo duplicado de cada punto. "
               "La celda f[zᵢ, zᵢ₊₁] del nodo duplicado es la derivada ingresada.")
    df = construir_tabla_df(z, Q)
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Polinomio de Hermite H(x) sin reducir")
    st.code(formato_polinomio(z, Q))
    st.subheader("Polinomio de Hermite H(x) reducido")
    st.code(formato_polinomio_reducido(z, Q))

    # --- Evaluación con validación de rango ---
    st.subheader("Evaluar el polinomio")
    x_min = min(x)
    x_max = max(x)
    st.caption(f"Rango con mayor precisión de interpolación: [{x_min}, {x_max}]")
    xp = st.number_input("Valor a interpolar (x)")

    if st.button("Evaluar"):
            resultado = evaluar_hermite(z, Q, xp)
            st.success(f"H({xp}) = {resultado}")

            x_vals = np.linspace(x_min, x_max, 200)
            y_vals = [evaluar_hermite(z, Q, xi) for xi in x_vals]

            fig, ax = plt.subplots()
            ax.plot(x_vals, y_vals)
            ax.scatter(x, y)
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