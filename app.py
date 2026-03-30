import streamlit as st
from streamlit.source_util import page_icon_and_name

st.sidebar.title("Seleccione un método de interpolación")
st.set_page_config(page_title='Interpolacion 2026', page_icon="images/ues.ico")

st.title("Interpolación")
st.write("Bienvenidos, en esta pagina podran realizar de manera eficiente y satisfactoria problemas que requieron uso de interpolación")
st.image("images/InLin.png", caption="Interpolación Lineal", width=600)
st.write("En esta pagina se encuentran los siguientes metodos de interpolación:")
st.markdown("""
### Interpolación Polinómica
- Lagrange
- Newton
  - Hacia Adelante
  - Hacia Atrás
- Diferencias Lineales
  - Stirling
  - Bessel
- Polinomio de Hermite

### Interpolación por Tramos
- Spline Lineal
- Spline Cuadrática
- Spline Cúbico
""")