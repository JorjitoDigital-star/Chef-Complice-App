import streamlit as st
import google.generativeai as genai

# 1. INTERFAZ SIMPLE Y PROFESIONAL
st.set_page_config(page_title="Chefcito 👨‍🍳")
st.title("👨‍🍳 Chefcito")

# 2. CONEXIÓN
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets de Streamlit.")
    st.stop()

# --- DIAGNÓSTICO (Solo para ver en la consola negra) ---
try:
    print("--- MODELOS DISPONIBLES EN ESTE SERVIDOR ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Disponible: {m.name}")
except:
    pass
# -------------------------------------------------------

# 3. EL "VIEJO CONFIABLE": GEMINI-PRO
# Este modelo es el que menos errores 404 da en todo el mundo.
try:
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Error al inicializar: {e}")

# 4. CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy Chefcito. 👨‍🍳 Es un gusto saludarle. ¿Qué ingredientes tenemos hoy?"})

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Escriba su consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Instrucciones de comportamiento inyectadas directamente
    instrucciones = (
        "Actúa como Chefcito, experto culinario profesional con 15 años de experiencia. "
        "Usa gramática perfecta y trato respetuoso. ESTÁ PROHIBIDO ser cursi o usar apodos. "
        "Si es una receta, usa el formato: Nombre, Valor Nutritivo, Pasos y Toque Maestro. "
        "Responde a lo siguiente: "
    )
    
    try:
        # Respuesta directa
        response = model.generate_content(instrucciones + prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        # Si esto falla, nos dirá el error real sin rodeos
        st.error(f"Inconveniente técnico: {e}")
