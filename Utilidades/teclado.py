import streamlit as st

def render_teclado():
    # Estilo profesional adaptable
    st.markdown("""
        <style>
        div.stButton > button {
            width: 100%; height: 42px;
            border-radius: 8px; font-weight: 600;
            background-color: rgba(151, 166, 195, 0.15);
            border: 1px solid rgba(151, 166, 195, 0.3);
            font-size: 14px;
        }
        .function-display-box {
            background-color: #1e293b; color: #38bdf8;
            padding: 15px; border-radius: 10px;
            font-size: 24px; font-family: monospace;
            text-align: right; margin-bottom: 10px;
            border: 1px solid #334155; min-height: 60px;
            display: flex; align-items: center; justify-content: flex-end;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'func_str' not in st.session_state:
        st.session_state.func_str = ""

    def presionar_boton(valor_tecla):
        actual = st.session_state.func_str

        # Lógica especial para funciones específicas
        if valor_tecla == "AC":
            st.session_state.func_str = ""
        elif valor_tecla == "⌫":
            st.session_state.func_str = actual[:-1]
        elif valor_tecla == "sqrt":
            st.session_state.func_str = actual + "sqrt("
        elif valor_tecla == "root_n":
            # Para SymPy, raíz n-ésima es (x)**(1/n)
            # Dejamos la estructura lista para que el usuario rellene
            st.session_state.func_str = actual + "**(1/"
        elif valor_tecla == "x²":
            st.session_state.func_str = actual + "**2"
        elif valor_tecla == "π":
            st.session_state.func_str = actual + "pi"
        elif valor_tecla in ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log"]:
            st.session_state.func_str = actual + f"{valor_tecla}("
        else:
            st.session_state.func_str = actual + str(valor_tecla)

    # Pantalla
    st.markdown(f'<div class="function-display-box">{st.session_state.func_str if st.session_state.func_str else "0"}</div>', unsafe_allow_html=True)

    # Layout actualizado (7 columnas para que sea simétrico)
    layout = [
        ["asin", "acos", "atan", "ln", "log", "sqrt", "root_n"],
        ["sin", "cos", "tan", "e", "π", "(", ")"],
        ["7", "8", "9", "/", "^", "x", "x²"],
        ["4", "5", "6", "*", "y", "z", "⌫"],
        ["1", "2", "3", "-", "0", ".", "AC"],
        ["+", "%", ",", " ", " ", " ", " "] # Espacios vacíos para completar la fila si es necesario
    ]

    # Etiquetas visuales bonitas
    labels = {
        "asin": "sin⁻¹",
        "acos": "cos⁻¹",
        "atan": "tan⁻¹",
        "sqrt": "√",
        "root_n": "ⁿ√",
        "x²": "x²",
        "^": "xⁿ",
        "π": "π",
        "⌫": "⌫",
        "AC": "AC"
    }

    for row in layout:
        cols = st.columns(7)
        for i, tecla in enumerate(row):
            if tecla.strip(): # Solo dibuja si no es un espacio vacío
                texto_mostrar = labels.get(tecla, tecla)
                cols[i].button(texto_mostrar, key=f"btn_{tecla}_{i}_{row[0]}",
                               on_click=presionar_boton, args=(tecla,))