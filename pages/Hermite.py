import streamlit as st
st.title("Interpolacion por Polinomio de Hermite")
text = st.text_input("Aun estamos trabajando, puede escribir lo que guste :)")
send = st.button("Probar")
if send:
    st.success("¡Funciona! Gracias por probarlo :)")
    st.write(f"usted escribio: {text}")
