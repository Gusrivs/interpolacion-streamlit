import streamlit as st
def ingresar_puntos():
    n = int(st.number_input("Cantidad de puntos", min_value=2, step=1, value=2))
    x = []
    y = []
    for i in range(n):
        col1, col2 = st.columns(2)
        with col1:
            xi = st.number_input(f"x{i}", key=f"x{i}")
        with col2:
            yi = st.number_input(f"y{i}", key=f"y{i}")
        x.append(float(xi))
        y.append(float(yi))
    return x, y
