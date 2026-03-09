import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: 24px para lectura cómoda y profesional
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN AL MOTOR 2.5 FLASH
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configura la GOOGLE_API_KEY en los Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-2.5-flash')

# 3. IDENTIDAD Y REGLAS MAESTRAS (Prompt Engineering)
instrucciones_maestras = (
    "Eres 'Tu Chefcito', un experto culinario global. Habla en PRIMERA PERSONA.\n\n"
    "REGLAS CRÍTICAS DE COMPORTAMIENTO:\n"
    "* IDENTIDAD: Eres un asistente universal. PROHIBIDO decir que eres de Perú o de cualquier país específico. Te adaptas a la región del usuario.\n"
    "* CONTROL DE SALIDA: Si el usuario se despide (gracias, adiós, eso es todo), SOLO despídete cordialmente de forma breve. NO generes recetas nuevas en ese caso.\n"
    "* FORMATO: Cada párrafo, ingrediente o paso DEBE comenzar con una viñeta (*).\n"
    "* NUTRICIÓN: Fusiona el balance 50% vegetales / 25% proteína / 25% carbohidratos con el valor nutricional en un solo bloque de máximo 4 líneas.\n"
    "* LENGUAJE SENSORIAL: Describe colores (ej. 'ajo color arena'), aromas (ej. 'perfume cítrico') y texturas (ej. 'piel crujiente como cristal').\n"
    "* PROHIBICIÓN: Prohibido usar metáforas poéticas como 'danza de sabores' o 'atardecer líquido'. Sé técnico y descriptivo.\n"
    "* BREVEDAD: Máximo 25 palabras por cada paso de preparación.\n"
    "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
)

# 4. GESTIÓN DEL HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte hoy, dime:\n\n"
        "* ¿En qué **país o región** te encuentras?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÓGICA DE RESPUESTA CON EFECTO MÁQUINA DE ESCRIBIR
if prompt := st.chat_input("Dime qué tienes en tu cocina..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Preparamos el contexto completo
        full_prompt = f"{instrucciones_maestras}\n\nUsuario: {prompt}"
        
        try:
            # Activamos el streaming para el efecto de máquina de escribir
            response = model.generate_content(full_prompt, stream=True)
            
            placeholder = st.empty()
            full_text = ""
            
            for chunk in response:
                full_text += chunk.text
                # Mostramos el texto acumulado con un pequeño retraso para suavizar el efecto
                placeholder.markdown(full_text + "▌")
                time.sleep(0.01)
            
            placeholder.markdown(full_text)
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            st.error(f"Error técnico: {e}")
