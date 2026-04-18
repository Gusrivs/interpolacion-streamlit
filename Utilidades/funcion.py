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
    """Evalúa una expresión sympy en un punto numérico."""
    x = sp.Symbol('x')
    try:
        return float(expr.subs(x, xval).evalf())
    except Exception:
        return None


def generar_puntos(expr, a: float, b: float, n: int):
    """
    Genera n puntos equiespaciados en [a, b] evaluando expr.
    Retorna (xs, ys) como listas de floats.
    """
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
            st.error(f"⚠️ {error}")
            return resultado

        st.write("**Vista previa matemática:**")
        st.latex(f"f(x) = {sp.latex(expr)}")

        resultado["expr"] = expr
        resultado["expr_str"] = expr_str

        st.markdown("---")
        st.markdown("####  Parámetros para los puntos")

        col1, col2, col3 = st.columns(3)
        with col1: a = st.number_input("Inicio (a)", value=0.0, key=f"{key_prefix}_a")
        with col2: b = st.number_input("Fin (b)", value=5.0, key=f"{key_prefix}_b")
        with col3: n = int(st.number_input("Nº de Puntos", min_value=2, max_value=20, value=5, key=f"{key_prefix}_n"))

        xs_base = np.linspace(a, b, n)
        xs_personalizados = []

    # --- AJUSTE DE VALORES X ---
    st.write("✍️ **Ajusta los valores de X si lo deseas:**")
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
    boton_presionado = st.button("🚀 Generar Tabla y Validar Puntos", use_container_width=True)
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

            st.success("✅ Puntos cargados correctamente")
            st.table(df)

            resultado.update({
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