import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras grandes y gramática clara para móvil
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Fuente clara y grande para lectura cómoda en personas mayores */
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #333333;
    }
    /* El Recetario: Destacado, legible y elegante */
    .recetario-chef {
        font-size: 26px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        margin-top: 15px;
        color: #000000;
    }
    /* Títulos destacados sin ser exagerados */
    .recetario-chef h2 {
        font-size: 30px !important;
        color: #FF4B4B !important;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA TURBO DE LA BIBLIOTECA (Máxima velocidad de respuesta)
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                texto_total += pagina.extract_text() + "\n"
                if len(texto_total) > 50000: break # Límite para velocidad óptima
        except:
            continue
    return texto_total[:50000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Por favor, configura la GOOGLE_API_KEY en los Secrets.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. HISTORIAL CON MEMORIA DE DIÁLOGO
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo_inicial = "¡Hola! Soy Chef-cito. 👨‍🍳✨ ¡Qué alegría encontrarte! Cuéntame, ¿de dónde nos escribes y qué tienes hoy en tu cocina?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA INTELIGENTE Y EFECTO DE ESCRITURA
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de comportamiento corregidas
        instruccion = (
            f"Eres 'Chef-cito (15 años de exp.)'. Hablas con personas mayores de forma dulce, breve y respetuosa. "
            f"Usa tus libros como referencia técnica ({conocimiento_pdf}) pero busca siempre en la web información actualizada. "
            f"REGLAS DE ORO:\n"
            f"1. GRAMÁTICA: Usa siempre Mayúsculas al iniciar cada oración y después de cada punto.\n"
            f"2. DIÁLOGO NATURAL: No repitas 'soy tu chef-cito' ni 'qué alegría' si ya están hablando. Varía tus frases como un amigo real.\n"
            f"3. COMENSALES: Si el usuario no menciona para cuántos es, PREGÚNTALE amablemente antes de dar la receta.\n"
            f"4. SALUD: Si piden algo para el malestar estomacal, ofrece infusiones o caldos ligeros. ¡Nunca comidas pesadas!\n"
            f"5. DESPEDIDA: Si dicen 'no', 'gracias' o 'eso es todo', despídete con amor y NO des más recetas.\n"
            f"6. FORMATO RECETA: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"7. CIERRE: Siempre termina preguntando si desean preparar algún otro platillo."
        )

        try:
            # Generación fluida de texto
            response = model.generate_content([instruccion, str(st.session_state.messages)], stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04) # Velocidad de lectura humana

            # Efecto máquina de escribir
            full_response = st.write_stream(stream_data())
            
            # Formateo visual del recetario (solo si es una receta real)
            if "Paso a Paso" in full_response and len(full_response) > 150:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            # Respuesta de respaldo en caso de error técnico
            despedida_error = "¡Fue un gusto cocinar contigo! Vuelve pronto a mi cocina cuando quieras. 👨‍🍳"
            st.write(despedida_error)
            st.session_state.messages.append({"role": "assistant", "content": despedida_error})
