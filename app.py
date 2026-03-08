import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Profesional, limpio y con letras para celular
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Letra grande y legible para evitar fatiga visual */
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #333333;
    }
    /* Recetario: Formato profesional y destacado */
    .recetario-chef {
        font-size: 24px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #FF4B4B;
        margin-top: 10px;
        color: #000000;
    }
    .recetario-chef h2 {
        font-size: 28px !important;
        color: #FF4B4B !important;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. CARGA DE BIBLIOTECA (Optimizada para estabilidad)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages:
                extraido = pag.extract_text()
                if extraido:
                    texto += extraido + "\n"
                if len(texto) > 35000: break 
        except: continue
    return texto[:35000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la configuración de seguridad (API Key).")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. MEMORIA DEL CHAT (Limpieza de etiquetas HTML para evitar errores)
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo_inicial = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, cuénteme de qué lugar nos escribe y qué ingredientes tiene disponibles hoy."
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA PROFESIONAL
if prompt := st.chat_input("Escriba su consulta aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones estrictas de comportamiento
        instruccion = (
            f"Eres 'Chefcito (15 años de exp.)'. Te diriges a personas mayores de forma respetuosa y profesional. "
            f"ESTÁ PROHIBIDO usar términos como 'mi vida', 'mi cielo', 'corazón' o similares. "
            f"Referencia técnica: {conocimiento_pdf}. Usa también información actualizada de la web.\n"
            f"REGLAS:\n"
            f"1. GRAMÁTICA: Usa siempre Mayúsculas al iniciar cada oración y después de cada punto.\n"
            f"2. COMENSALES: Si el usuario no indica para cuántos cocinará, pregunte amablemente antes de dar cantidades.\n"
            f"3. FLUIDEZ: No repita saludos. Si ya están conversando, sea directo y servicial.\n"
            f"4. DESPEDIDA: Si el usuario termina la charla, despídase formalmente sin ofrecer más recetas.\n"
            f"5. FORMATO RECETA: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro.\n"
            f"6. Siempre cierre preguntando si requiere asistencia con algún otro platillo."
        )

        try:
            # Creamos un historial limpio (sin etiquetas HTML) para que la IA no se confunda
            historial_limpio = ""
            for m in st.session_state.messages[-3:]:
                texto = m['content'].replace('<div class="recetario-chef">', '').replace('</div>', '')
                historial_limpio += f"{m['role']}: {texto}\n"

            # Generación con flujo de datos (Stream)
            response = model.generate_content([instruccion, historial_limpio, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04)

            # Efecto máquina de escribir
            full_response = st.write_stream(stream_data())
            
            # Formateo visual del recetario
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error("Se produjo un inconveniente en la comunicación. Por favor, intente enviar su mensaje nuevamente.")
