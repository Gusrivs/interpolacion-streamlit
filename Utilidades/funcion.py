import streamlit as st
import sympy as sp
import numpy as np
import pandas as pd
import re
from .teclado import render_teclado

# Locals seguros para parsear funciones del usuario
LOCALS_SEGUROS = {
    "ln": sp.log,
    "log": sp.log,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "exp": sp.exp,
    "sqrt": sp.sqrt,
    "abs": sp.Abs,
    "pi": sp.pi,
    "e": sp.E,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
}

EJEMPLOS = [
    "ln(x)",
    "sin(x)",
    "cos(x)",
    "tan(x)"
    "exp(x)",
    "x**(1/2)",
    "sqrt(x)",
    "1 / (1 + x**2)",
]


def parsear_funcion(expr_str: str):
    try:
        # 1. LIMPIEZA PREVIA (Pre-procesamiento)
        # Reemplaza 'x' pegada a números: '8x' -> '8*x'
        expr_str = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expr_str)

        # Reemplaza paréntesis pegados: ')( ' -> ')*(' o 'x(' -> 'x*('
        expr_str = re.sub(r'([x\)])(\()', r'\1*\2', expr_str)

        # Corregir potencias si el usuario usa ^ en lugar de **
        expr_str = expr_str.replace('^', '**')

        # 2. PARSEO CON SYMPY
        x = sp.Symbol('x')
        # Usamos 'transformations' de sympy para que sea aún más inteligente
        from sympy.parsing.sympy_parser import (
            parse_expr,
            standard_transformations,
            implicit_multiplication_application
        )

        # Esto permite que SymPy entienda "8x" o "sin x" automáticamente
        transformaciones = standard_transformations + (implicit_multiplication_application,)

        expr = parse_expr(expr_str, local_dict=LOCALS_SEGUROS, transformations=transformaciones)

        return expr, None
    except Exception as e:
        return None, f"Error de sintaxis: {e}"


def evaluar_funcion(expr, xval: float):
    x = sp.Symbol('x')
    try:
        return float(expr.subs(x, xval).evalf(15))
    except Exception:
        return None


def generar_puntos(expr, a: float, b: float, n: int):
    xs = np.linspace(a, b, n)
    ys = []
    for xi in xs:
        yi = evaluar_funcion(expr, xi)
        if yi is None:
            raise ValueError(f"La función no pudo evaluarse en x={xi}")
        ys.append(yi)
    return xs.tolist(), ys


def entrada_funcion_con_teclado(key_prefix: str = "func"):
    a, b, n = 0.0, 5.0, 5
    def al_cambiar_ejemplo():
        nueva_seleccion = st.session_state[f"{key_prefix}_selector_raw"]
        if nueva_seleccion:
            st.session_state.func_str = nueva_seleccion
    resultado = {
        "expr": None, "expr_str": "",
        "x_vals": None, "y_vals": None,
        "a": None, "b": None, "n": None,
        "valida": False
    }
    st.markdown("#### Configuración de la Función")
    # 1. Organización en pestañas
    tab_teclado, tab_ejemplos = st.tabs([" Teclado Visual", "📚 Ejemplos"])
    with tab_ejemplos:
        st.selectbox(
            "Seleccioná una función de ejemplo",
            [""] + EJEMPLOS,
            key=f"{key_prefix}_selector_raw",
            on_change=al_cambiar_ejemplo # <--- LA SOLUCIÓN
        )
    with st.expander("Teclado ", expanded=True):
        render_teclado()
        def actualizar_desde_manual():
            key_manual = f"{key_prefix}_manual"
            if key_manual in st.session_state:
                st.session_state.func_str = st.session_state[key_manual]
        st.text_input(
            "Edición manual (escribe y presiona Enter):",
            value=st.session_state.get('func_str', ""),
            key=f"{key_prefix}_manual",
            on_change=actualizar_desde_manual
        )
    expr_str = st.session_state.get('func_str', "")
    if expr_str:
        expr, error = parsear_funcion(expr_str)
        if error:
            #st.error(f"⚠️ {error}")
            st.caption("✏️ Completa la función para ver la vista previa…")
            return resultado
        st.write("**Vista previa matemática:**")
        st.latex(f"f(x) = {sp.latex(expr)}")
        resultado["expr"] = expr
        resultado["expr_str"] = expr_str
        st.markdown("---")
        st.markdown("####  Parámetros para los puntos")
        n = int(st.number_input("Nº de Puntos", min_value=2, max_value=20, value=5, key=f"{key_prefix}_n"))
        a = 0
        b = 5
        xs_base = np.linspace(a, b, n)
        xs_personalizados = []
    # --- AJUSTE DE VALORES X ---
    st.write("**Valores de X:**")
    xs_base = np.linspace(a, b, n)
    cols_x = st.columns(min(n, 5))
    xs_personalizados = []
    for i in range(n):
        with cols_x[i % 5]:
            # Aseguramos que el valor inicial sea float para evitar conflictos
            val_x = st.number_input(f"x_{i}", value=float(xs_base[i]), key=f"{key_prefix}_xi_{i}")
            xs_personalizados.append(val_x)
    # --- BOTÓN DE ACCIÓN CON PROTECCIÓN ---
    # Usamos .get() para evitar el KeyError/TypeError si la llave no existe aún
    boton_presionado = st.button("Generar Tabla y Validar Puntos", use_container_width=True)
    ya_estaba_listo = st.session_state.get(f"{key_prefix}_puntos_listos", False)

    if boton_presionado or ya_estaba_listo:
        try:
            # Verificación de seguridad: ¿Existe la expresión?
            if expr is None:
                st.warning("Primero ingresa una función válida.")
                return resultado

            ys = [evaluar_funcion(expr, xi) for xi in xs_personalizados]

            # Filtramos valores None por si acaso la evaluación falló en algún punto
            if any(y is None for y in ys):
                st.error("La función no se pudo evaluar en algunos puntos. Revisa la expresión.")
                return resultado

            df = pd.DataFrame({"x": xs_personalizados, "f(x)": ys})

            st.success("Puntos cargados correctamente")
            st.table(df)

            resultado.update({
                "f" : lambda xval: evaluar_funcion(expr, xval),
                "expr": expr,
                "expr_str": expr_str,
                "x_vals": xs_personalizados,
                "y_vals": ys,
                "a": a, "b": b, "n": n,
                "valida": True
            })

            st.session_state[f"{key_prefix}_puntos_listos"] = True

        except Exception as e:
            st.error(f"Error al evaluar puntos: {e}")
            st.session_state[f"{key_prefix}_puntos_listos"] = False

    return resultado


def error_relativo(f_real: float, f_aprox: float) -> float:
    """Calcula el error relativo porcentual entre el valor real y el aproximado."""
    if f_real == 0:
        return None  # indefinido
    return abs((f_real - f_aprox) / f_real) * 100

def entrada_hermite_con_teclado(key_prefix: str = "hermite"):
    """
    Igual que entrada_funcion_con_teclado pero además calcula
    derivadas simbólicas y retorna 'derivadas' para tabla_hermite().
    """
    x_sym = sp.Symbol('x')

    def al_cambiar_ejemplo():
        nueva_seleccion = st.session_state[f"{key_prefix}_selector_raw"]
        if nueva_seleccion:
            st.session_state.func_str = nueva_seleccion

    resultado = {
        "expr": None, "expr_str": "",
        "x_vals": None, "y_vals": None,
        "derivadas": None, "f": None,
        "valida": False
    }

    st.markdown("#### Configuración de la Función")

    tab_teclado, tab_ejemplos = st.tabs(["⌨️ Teclado Visual", "📚 Ejemplos"])
    with tab_ejemplos:
        st.selectbox(
            "Seleccioná una función de ejemplo",
            [""] + EJEMPLOS,
            key=f"{key_prefix}_selector_raw",
            on_change=al_cambiar_ejemplo
        )
    with tab_teclado:
        render_teclado()  # ← el mismo teclado original, usa func_str global igual que Lagrange
        def actualizar_desde_manual():
            key_manual = f"{key_prefix}_manual"
            if key_manual in st.session_state:
                st.session_state.func_str = st.session_state[key_manual]
        st.text_input(
            "Edición manual (escribe y presiona Enter):",
            value=st.session_state.get('func_str', ""),
            key=f"{key_prefix}_manual",
            on_change=actualizar_desde_manual
        )

    expr_str = st.session_state.get('func_str', "")

    if not expr_str:
        return resultado

    expr, error = parsear_funcion(expr_str)
    if error:
        st.caption("✏️ Completa la función para ver la vista previa…")
        return resultado

    st.write("**Vista previa matemática:**")
    st.latex(f"f(x) = {sp.latex(expr)}")
    resultado["expr"] = expr
    resultado["expr_str"] = expr_str

    st.markdown("---")
    st.markdown("#### Parámetros")

    col1, col2 = st.columns(2)
    with col1:
        n = int(st.number_input("Nº de puntos", min_value=2, max_value=20, value=3,
                                 key=f"{key_prefix}_n"))
    with col2:
        nd = int(st.number_input("Orden máximo de derivada", min_value=1, max_value=5, value=1,
                                  key=f"{key_prefix}_nd"))

    # Mostrar derivadas simbólicas calculadas
    derivadas_simbolicas = {orden: sp.diff(expr, x_sym, orden) for orden in range(1, nd + 1)}
    with st.expander("📐 Derivadas calculadas automáticamente"):
        for orden, d_expr in derivadas_simbolicas.items():
            st.latex(f"f^{{({orden})}}(x) = {sp.latex(d_expr)}")

    st.write("**Valores de X:**")
    xs_base = np.linspace(0, 1, n)
    cols_x = st.columns(min(n, 5))
    xs_personalizados = []
    for i in range(n):
        with cols_x[i % 5]:
            val_x = st.number_input(f"x_{i}", value=float(xs_base[i]),
                                     key=f"{key_prefix}_xi_{i}")
            xs_personalizados.append(val_x)

    boton_presionado  = st.button("Generar puntos y derivadas", use_container_width=True,
                                   key=f"{key_prefix}_generar")
    ya_estaba_listo   = st.session_state.get(f"{key_prefix}_puntos_listos", False)

    if boton_presionado or ya_estaba_listo:
        try:
            ys = [evaluar_funcion(expr, xi) for xi in xs_personalizados]
            if any(yi is None for yi in ys):
                st.error("La función no se pudo evaluar en algunos puntos.")
                return resultado

            derivadas = {}
            for i, xi in enumerate(xs_personalizados):
                derivadas[i] = {}
                for orden, d_expr in derivadas_simbolicas.items():
                    val = evaluar_funcion(d_expr, xi)
                    if val is not None:
                        derivadas[i][orden] = val

            filas_prev = []
            for i, xi in enumerate(xs_personalizados):
                fila = {"x": round(xi, 6), "f(x)": round(ys[i], 6)}
                for orden in range(1, nd + 1):
                    fila[f"f^({orden})(x)"] = round(derivadas[i].get(orden, 0), 6)
                filas_prev.append(fila)

            st.success("Puntos y derivadas generados correctamente")
            st.dataframe(pd.DataFrame(filas_prev), use_container_width=True)

            resultado.update({
                "f":         lambda xval: evaluar_funcion(expr, xval),
                "expr":      expr,
                "expr_str":  expr_str,
                "x_vals":    xs_personalizados,
                "y_vals":    ys,
                "derivadas": derivadas,
                "valida":    True
            })
            st.session_state[f"{key_prefix}_puntos_listos"] = True

        except Exception as e:
            st.error(f"Error al generar puntos: {e}")
            st.session_state[f"{key_prefix}_puntos_listos"] = False

    return resultado
    """
    Versión del teclado que usa func_str prefijado para no
    colisionar con el teclado de Lagrange/Newton.
    """
    from .teclado import render_teclado as _base

    key_str = f"{key_prefix}_func_str"
    if key_str not in st.session_state:
        st.session_state[key_str] = ""

    def presionar_boton(valor_tecla):
        actual = st.session_state[key_str]
        if valor_tecla == "AC":
            st.session_state[key_str] = ""
        elif valor_tecla == "⌫":
            st.session_state[key_str] = actual[:-1]
        elif valor_tecla == "sqrt":
            st.session_state[key_str] = actual + "sqrt("
        elif valor_tecla == "root_n":
            st.session_state[key_str] = actual + "**(1/"
        elif valor_tecla == "x²":
            st.session_state[key_str] = actual + "**2"
        elif valor_tecla == "^":
            st.session_state[key_str] = actual + "**"
        elif valor_tecla == "π":
            st.session_state[key_str] = actual + "pi"
        elif valor_tecla in ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log"]:
            st.session_state[key_str] = actual + f"{valor_tecla}("
        else:
            st.session_state[key_str] = actual + str(valor_tecla)

    st.markdown(
        f'<div class="function-display-box">'
        f'{st.session_state[key_str] if st.session_state[key_str] else "0"}'
        f'</div>',
        unsafe_allow_html=True
    )

    layout = [
        ["asin", "acos", "atan", "ln", "log", "sqrt", "root_n"],
        ["sin", "cos", "tan", "e", "π", "(", ")"],
        ["7", "8", "9", "/", "^", "x", "x²"],
        ["4", "5", "6", "*", "y", "z", "⌫"],
        ["1", "2", "3", "-", "0", ".", "AC"],
        ["+", "%", ",", None, None, None, None],
    ]
    labels = {
        "asin": "sin⁻¹", "acos": "cos⁻¹", "atan": "tan⁻¹",
        "sqrt": "√", "root_n": "ⁿ√", "x²": "x²",
        "^": "xⁿ", "π": "π", "⌫": "⌫", "AC": "AC"
    }
    for fila_idx, row in enumerate(layout):
        cols = st.columns(7)
        for i, tecla in enumerate(row):
            if tecla is None:
                cols[i].empty()
                continue
            texto_mostrar = labels.get(tecla, tecla)
            cols[i].button(
                texto_mostrar,
                key=f"{key_prefix}_btn_{fila_idx}_{i}_{tecla}",
                on_click=presionar_boton,
                args=(tecla,),
                use_container_width=True,
            )