import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras grandes para celular y gramática profesional
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Fuente clara y grande para lectura cómoda */
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #333333;
    }
    /* El Recetario: Destacado pero ajustable a la pantalla del móvil */
    .recetario-chef {
        font-size: 26px !important;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #FF4B4B;
        margin-top: 10px;
        color: #000000;
        font-weight: normal;
    }
    /* Títulos con jerarquía correcta */
    .recetario-chef h2 {
        font-size: 28px !important;
        color: #FF4B4B !important;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA ULTRA-RÁPIDA (Limitada a 50k para ganar velocidad)
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                texto_total += pagina.extract_text() + "\n"
                if len(texto_total) > 50000: break
        except:
            continue
    return texto_total[:50000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Por favor, verifica la configuración de la llave secreta.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. HISTORIAL CON MEMORIA DINÁMICA
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡Hola! Soy Chef-cito. 👨‍🍳✨ ¡Qué alegría encontrarte! Cuéntame, ¿de dónde nos escribes y qué tienes hoy en tu cocina?"
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE DIÁLOGO INTELIGENTE
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de personalidad y lógica de flujo
        instruccion = (
            f"Eres 'Chef-cito (15 años de exp.)'. Hablas con personas mayores de forma dulce y respetuosa. "
            f"Usa tus libros como referencia técnica ({conocimiento_pdf}) pero busca siempre en la web información actualizada. "
            f"REGLAS CRÍTICAS:\n"
            f"1. GRAMÁTICA: Usa siempre Mayúsculas al iniciar oraciones y después de cada punto.\n"
            f"2. SIN REPETICIONES: No digas siempre 'qué alegría' o 'soy tu chef-cito'. Si ya están hablando, mantén la charla fluida como un amigo.\n"
            f"3. COMENSALES: Si el usuario no dice para cuántas personas es, PREGÚNTALE amablemente antes de dar cantidades exactas.\n"
            f"4. SALUD/INFUSIONES: Si piden algo para el malestar, sugiere infusiones o caldos suaves. ¡No des recetas pesadas como carnes o humitas!\n"
            f"5. DESPEDIDA: Si el usuario dice 'no', 'eso es todo' o 'gracias', despídete con amor y no des más recetas.\n"
            f"6. FORMATO RECETA: Si das una receta, incluye: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso (con verbos inspiradores), Residuo Cero, Plus y Toque Maestro.\n"
            f"7. TERMINA siempre preguntando si desea preparar algo más."
        )

        try:
            # Generación con efecto de escritura palabra por palabra
            response = model.generate_content([instruccion, str(st.session_state.messages)], stream=True)
            
            def stream_data():
                for chunk in response:
                    for word in chunk.text.split(" "):
                        yield word + " "
                        time.sleep(0.05)

            # Mostramos el flujo de texto
            full_response = st.write_stream(stream_data())
            
            # Aplicamos el diseño del recetario si detectamos una receta
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error("¡Vaya! Tuvimos un pequeño tropiezo en la cocina. ¿Me lo repites?")
