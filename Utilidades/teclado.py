import streamlit as st

def render_teclado():
    # Estilo profesional adaptable
    st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            height: 42px;
            min-height: 42px;
            border-radius: 8px;
            font-weight: 600;
            background-color: rgba(151, 166, 195, 0.15);
            border: 1px solid rgba(151, 166, 195, 0.3);
            font-size: 14px;
            padding: 0;
            line-height: 1;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        /* Quita el gap por defecto entre columnas para que los botones
           queden parejos y pegados, sin que el ancho varíe entre filas */
        div[data-testid="stHorizontalBlock"] {
            gap: 4px;
            /* Streamlit apila las columnas verticalmente en pantallas
               angostas (responsive por defecto). Esto lo evita: las
               7 columnas se mantienen siempre en una sola fila. */
            flex-wrap: nowrap !important;
            flex-direction: row !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            min-width: 0 !important;
            flex: 1 1 0 !important;
            width: auto !important;
        }
        .function-display-box {
            background-color: #1e293b; color: #38bdf8;
            padding: 15px; border-radius: 10px;
            font-size: 24px; font-family: monospace;
            text-align: right; margin-bottom: 10px;
            border: 1px solid #334155; min-height: 60px;
            display: flex; align-items: center; justify-content: flex-end;
            word-break: break-all;
        }
        @media (max-width: 768px) {
            .function-display-box { font-size: 16px !important; }
            div.stButton > button {
                font-size: 10px;
                height: 34px;
                min-height: 34px;
                padding: 0 1px;
                border-radius: 6px;
            }
            div[data-testid="stHorizontalBlock"] { gap: 2px; }
        }
        @media (max-width: 480px) {
            div.stButton > button {
                font-size: 9px;
                height: 30px;
                min-height: 30px;
            }
            div[data-testid="stHorizontalBlock"] { gap: 1px; }
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
        elif valor_tecla == "^":
            st.session_state.func_str = actual + "**"
        elif valor_tecla == "π":
            st.session_state.func_str = actual + "pi"
        elif valor_tecla in ["sin", "cos", "tan", "asin", "acos", "atan", "ln", "log"]:
            st.session_state.func_str = actual + f"{valor_tecla}("
        else:
            st.session_state.func_str = actual + str(valor_tecla)

    # Pantalla
    st.markdown(
        f'<div class="function-display-box">'
        f'{st.session_state.func_str if st.session_state.func_str else "0"}'
        f'</div>',
        unsafe_allow_html=True
    )

    # Layout actualizado (7 columnas para que sea simétrico)
    layout = [
        ["asin", "acos", "atan", "ln", "log", "sqrt", "root_n"],
        ["sin", "cos", "tan", "e", "π", "(", ")"],
        ["7", "8", "9", "/", "^", "x", "x²"],
        ["4", "5", "6", "*", "y", "z", "⌫"],
        ["1", "2", "3", "-", "0", ".", "AC"],
        ["+", "%", ",", None, None, None, None],
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

    for fila_idx, row in enumerate(layout):
        cols = st.columns(7)
        for i, tecla in enumerate(row):
            if tecla is None:
                # Celda vacía real: no dibuja ningún botón, mantiene la
                # columna ocupando su espacio para que el grid no se desalinee.
                cols[i].empty()
                continue
            texto_mostrar = labels.get(tecla, tecla)
            cols[i].button(
                texto_mostrar,
                key=f"btn_{fila_idx}_{i}_{tecla}",
                on_click=presionar_boton,
                args=(tecla,),
                use_container_width=True,
            )