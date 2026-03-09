import streamlit as st
import google.generativeai as genai

# Estilo visual de 24px para móviles
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# Conexión Directa y Estable
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Configura la API Key en los Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = ("¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para cocinar algo increíble hoy en **Perú**, dime: "
                  "¿Qué **país**?, ¿Qué **ingredientes**? y ¿Para **cuántos**?")
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tengo yuca, arroz y pollo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde en PRIMERA PERSONA.\n"
            "* Usa viñetas para cada párrafo.\n"
            "* Fusiona Nutrición y Balance 50/25/25 en un solo bloque breve.\n"
            "* Gramática fluida, sin palabras cortadas.\n"
            "* Cierre: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Quitamos el streaming para evitar el Error 400
            response = model.generate_content(instrucciones + prompt, stream=False)
            full_text = response.text
            
            st.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"Error crítico: {e}. Verifica la habilitación de la API.")
