import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. ESTILO VISUAL: Letras Gigantes para personas mayores
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Letra base muy grande para todo el chat */
    .stChatMessage, p, li, div {
        font-size: 28px !important;
        line-height: 1.5 !important;
    }
    /* El RECETARIO: Letra extra grande, negrita y destacada */
    .recetario-chef {
        font-size: 34px !important;
        font-weight: bold !important;
        color: #000000;
        background-color: #f9f9f9;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        margin-top: 20px;
    }
    /* Estilo para los títulos dentro de la receta */
    .recetario-chef h1, .recetario-chef h2, .recetario-chef h3 {
        font-size: 40px !important;
        color: #FF4B4B !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")
st.markdown("---")

# 2. CARGA ULTRA-RÁPIDA DE LOS LIBROS (Optimizado para velocidad)
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            # Leemos solo lo esencial para ganar esos 15 segundos de respuesta
            for i, pagina in enumerate(lector.pages):
                if i > 50: break # Límite de seguridad por libro
                texto_total += pagina.extract_text() + "\n"
        except:
            continue
    return texto_total[:80000] # Menos carga = Más velocidad

conocimiento_pdf = cargar_biblioteca()

# 3. CONEXIÓN CON EL MODELO (Usando la versión Flash para máxima rapidez)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Por favor, configura la API Key.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. MEMORIA Y DIÁLOGO NATURAL
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo inicial tierno
    bienvenida = (
        "¡Hola! Soy Chef-cito. 👨‍🍳✨\n\n"
        "¡Qué alegría verte! Cuéntame, ¿de dónde me escribes y qué tienes hoy en tu cocina?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. EL CEREBRO DE CHEF-CITO (Personalidad variable y creativa)
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Instrucción Maestra Dinámica
            instruccion_maestra = (
                f"Eres 'Chef-cito (15 años de exp.)'. Hablas con personas mayores de forma dulce y sencilla. "
                f"Usa tus libros ({conocimiento_pdf}) y la web para responder. "
                f"REGLAS DE ORO:\n"
                f"1. Si es el inicio de la charla, preséntate. Si ya están hablando, NO repitas 'Soy tu Chef-cito', sé natural.\n"
                f"2. Si das una receta, usa este formato dentro de un recuadro (div class='recetario-chef'):\n"
                f"   - Nombre del plato (¡Ponle un nombre creativo!)\n"
                f"   - Valor Nutritivo 💪\n"
                f"   - Proporciones (Regla 50/25/25)\n"
                f"   - Paso a Paso 🍳 (usa verbos como 'Sella la magia', 'Aroma regional')\n"
                f"   - Residuo Cero (consejo para no botar nada)\n"
                f"   - El Plus de Chef-cito 💡\n"
                f"   - Toque Maestro 🌟\n"
                f"3. Al terminar CUALQUIER respuesta, pregunta cariñosamente si desean preparar algo más.\n"
                f"4. Sé muy breve fuera del recetario. Letras grandes siempre."
            )
            
            # Generar respuesta
            response = model.generate_content([instruccion_maestra, prompt])
            
            # Si la respuesta parece una receta, le ponemos el diseño especial
            if "Paso a Paso" in response.text or "Regla" in response.text:
                final_text = f'<div class="recetario-chef">{response.text}</div>'
            else:
                final_text = response.text
            
            st.markdown(final_text, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": final_text})
            
        except Exception:
            st.error("¡Ay! La hornilla se apagó. ¿Me repites eso, por favor?")
