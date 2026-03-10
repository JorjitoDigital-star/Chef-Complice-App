import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: 24px para tu comodidad visual
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div, span {
        font-size: 24px !important;
        line-height: 1.4 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONFIGURACIÓN DE SEGURIDAD (API KEY)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configura la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# 3. EL "CEREBRO" DE TU CHEFCITO: Amable, Gentil y Divertido
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario global. Tu personalidad es amable, gentil y divertida.\n\n"
    "REGLAS DE IDENTIDAD Y MEMORIA:\n"
    "* Saludo: '¡Hola! Soy Tu Chefcito 👨‍🍳. Un cusicusa y estamos aquí...'. Úsalo solo en el primer mensaje.\n"
    "* Memoria: Revisa siempre el historial. Si ya conoces el país y comensales, no los preguntes de nuevo.\n"
    "* Validación: Si no sabes el país o comensales, pídelos con mucha gentileza antes de cocinar.\n\n"
    "REGLA DE CAMBIO DE CATEGORÍA:\n"
    "* Postres: Si piden postre y solo hay ingredientes salados (pollo, papas, etc.), detente amablemente y pide ingredientes dulces.\n"
    "* Platos extra: Pregunta si quieres usar lo que ya tenemos o tienes nuevos ingredientes.\n\n"
    "ESTILO DE RESPUESTA:\n"
    "* Formato: Usa viñetas para CADA párrafo y CADA paso de la receta.\n"
    "* Tono: Sé divertido y servicial. Evita frases excesivamente poéticas o cursis.\n"
    "* Tip de Experto: Incluye solo UN tip profesional por receta para no saturar.\n"
    "* Nutrición: Descripción breve con adjetivos. Prohibido usar números o el símbolo %.\n"
    "* Pasos: Breves y claros (máximo 20 palabras por paso).\n\n"
    "CIERRE CON CHISPA:\n"
    "* Si el usuario se despide o agradece, responde con cariño: '¡Fue un placer cocinar contigo! No dudes en llamarme cuando necesites otra mano en la cocina. Un cusicusa y estamos aquí'. No hagas más preguntas al cerrar."
)

model = genai.GenerativeModel(
    model_name='gemini-2.5-flash',
    system_instruction=instrucciones_maestras
)

# 4. GESTIÓN DEL CHAT CON MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Un cusicusa y estamos aquí... \n\n¿En qué país estás, qué tenemos en la cocina y para cuántos cocinamos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÓGICA DE INTERACCIÓN
if prompt := st.chat_input("Dime tus ingredientes o platillo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Construimos el historial para que no tenga amnesia
        history = [
            {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
            for m in st.session_state.messages[:-1]
        ]
        
        chat = model.start_chat(history=history)
        
        try:
            response = chat.send_message(prompt, stream=True)
            placeholder = st.empty()
            full_text = ""
            
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.01)
            
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"¡Chispazo técnico! {e}")
