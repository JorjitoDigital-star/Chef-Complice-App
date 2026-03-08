import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL (Limpio y profesional)
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li, div { font-size: 24px !important; color: #1A1A1A; }</style>", unsafe_allow_html=True)
st.title("👨‍🍳 Chefcito - Tu Chef Peruano")

# 2. CONEXIÓN SEGURA (Sin errores 400/404)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key.")
    st.stop()

@st.cache_resource
def configurar_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if p in modelos: return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

model = configurar_modelo()

# 3. CONOCIMIENTO (PDF)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    for arc in [f for f in os.listdir('.') if f.endswith('.pdf')]:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]: texto += pag.extract_text() + "\n"
        except: continue
    return texto[:15000]

biblioteca = cargar_biblioteca()

# 4. MEMORIA DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳 Es un gusto saludarte. Cuéntame, ¿desde dónde escribes y qué cocinamos hoy?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA (CONCISA Y SIN SÍLABAS SEPARADAS)
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIONES ESTRICTAS DE CALIDAD
        instrucciones = (
            f"Eres 'Chefcito', un Chef Senior amigable y divertido. Resuélvele al usuario de forma ÁGIL.\n"
            f"REGLAS CRÍTICAS:\n"
            f"1. GRAMÁTICA: Escribe de forma fluida. PROHIBIDO separar palabras con espacios (ej. no pongas 'Pol lo' o 'Pa pas'). Escribe todo de corrido y con mayúsculas tras los puntos.\n"
            f"2. BREVEDAD: No des discursos largos. Sé directo. Si es una receta, ve al grano.\n"
            f"3. COMENSALES: Si no sabes para cuántos es, PREGUNTA. Si ya lo sabes, no lo repitas.\n"
            f"4. FORMATO: Solo para el PLATO PRINCIPAL usa el formato (Nombre, Nutrición, 50/25/25, Pasos, Residuo Cero, Toque Maestro). Para acompañamientos, sopas o mates, sé muy breve (solo ingredientes y pasos cortos).\n"
            f"5. ORIGEN: Prioriza siempre el sabor de PERÚ. No inventes fusiones raras con el PDF ({biblioteca}) a menos que el usuario lo pida.\n"
            f"6. TONO: Divertido, amigable pero profesional. Nada de 'mi vida' o 'corazón'.\n\n"
        )
        
        try:
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_text():
                for chunk in response:
                    if chunk.text:
                        # Limpieza manual de espacios extraños que vienen del PDF
                        texto_limpio = chunk.text.replace("  ", " ")
                        for word in texto_limpio.split(" "):
                            yield word + " "
                            time.sleep(0.01)

            full_text = st.write_stream(stream_text())
            
            if "Paso a Paso" in full_text:
                output = f'<div style="background-color:#F9F9F9; padding:20px; border-radius:12px; border:2px solid #D0021B; box-shadow: 2px 2px 5px rgba(0,0,0,0.05);">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"Inconveniente: {e}")
