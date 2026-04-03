import streamlit as st

st.set_page_config(page_title="Interpolacion 2026", page_icon="images/Logo.ico", layout="centered")

st.title("Métodos de Interpolación")
st.image("images/Portada.png", width=550)


st.write("Responde el siguiente formulario y te sugeriremos el método más adecuado para tu caso.")
st.divider()

# --- Formulario ---
with st.form("formulario"):
    st.subheader("Cuéntanos sobre tus datos")

    conoce_derivada = st.radio(
        "¿Conocés el valor de la derivada en los puntos?",
        ["Sí", "No"],
        horizontal=True
    )

    espaciado_uniforme = st.radio(
        "¿Los puntos están igualmente espaciados (mismo Δx entre todos)?",
        ["Sí", "No"],
        horizontal=True
    )

    quiere_suavidad = st.radio(
        "¿Necesitás que la curva sea suave entre cada par de puntos (sin quiebres)?",
        ["Sí", "No"],
        horizontal=True
    )

    cantidad_puntos = st.radio(
        "¿Cuántos puntos tenés aproximadamente?",
        ["Pocos (2 - 5)", "Varios (6 o más)"],
        horizontal=True
    )

    enviado = st.form_submit_button("Sugerir método →")

# --- Lógica de sugerencia ---
if enviado:
    st.divider()
    st.subheader("Método sugerido")

    if conoce_derivada == "Sí":
        metodo     = "Hermite"
        descripcion = ("Conocés tanto f(x) como f'(x) en cada punto, "
                       "lo que permite a Hermite aproximar con mayor precisión "
                       "respetando la pendiente en cada nodo.")
        pagina      = "pages/Hermite.py"
        emoji      = "🔵"

    elif quiere_suavidad == "Sí":
        metodo      = "Spline"
        descripcion = ("Necesitás suavidad entre tramos, los Splines dividen "
                       "el intervalo en segmentos y garantizan continuidad "
                       "en la curva y sus derivadas. Podés elegir entre Lineal, "
                       "Cuadrático o Cúbico según el grado de precisión que necesités.")
        pagina      = "pages/Spline Lineal.py"
        emoji       = "🟠"

    elif espaciado_uniforme == "Sí":
        metodo      = "Diferencias Finitas (Bessel / Stirling)"
        descripcion = ("Tus puntos están igualmente espaciados, condición "
                       "necesaria para aplicar las fórmulas de Bessel y Stirling "
                       "que aprovechan ese espaciado para mayor eficiencia.")
        pagina      = "pages/Diferencias Finitas.py"
        emoji       = "🔴"

    else:
        if cantidad_puntos == "Pocos (2 - 5)":
            metodo      = "Lagrange"
            descripcion = ("Con pocos puntos y sin condiciones especiales, "
                           "Lagrange construye directamente el polinomio de "
                           "colocación de forma simple y clara.")
            pagina      = "pages/Lagrange.py"
            emoji       = "🔵"
        else:
            metodo      = "Newton"
            descripcion = ("Con varios puntos, Newton es más eficiente que Lagrange "
                           "gracias a las diferencias divididas: podés agregar puntos "
                           "sin recalcular todo el polinomio.")
            pagina      = "pages/Newton.py"
            emoji       = "🔵"

    # --- Tarjeta de resultado ---
    st.markdown(f"## {emoji} {metodo}")
    st.info(descripcion)

    st.markdown("### Todos los métodos disponibles")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.page_link("pages/Newton.py",              label="📘 Newton")
        st.page_link("pages/Lagrange.py",            label="📘 Lagrange")
        st.page_link("pages/Hermite.py",             label="📘 Hermite")

    with col2:
        st.page_link("pages/Diferencias Finitas.py", label="📕 Diferencias Finitas")

    with col3:
        st.page_link("pages/Spline Lineal.py",       label="📒 Spline Lineal")
        st.page_link("pages/Spline Cuadratica.py",   label="📒 Spline Cuadrático")
        st.page_link("pages/Splinen Cubico.py",      label="📒 Spline Cúbico")

    st.divider()
    st.markdown("<style>div[data-testid='stPageLink'] * {font-size: 20px; font-weight: bold}</style>", unsafe_allow_html=True)
    st.page_link(pagina, label=f"Ir a {metodo} → {emoji}")

