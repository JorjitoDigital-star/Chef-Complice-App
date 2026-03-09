import streamlit as st
import google.generativeai as genai

# Mantenemos tu formato de 24px para que lo veas claro
st.set_page_config(page_title="Scanner de Chefcito 🔍")
st.markdown("<style>p, li, div { font-size: 24px !important; }</style>", unsafe_allow_html=True)

st.title("🔍 Escáner de Modelos Permitidos")

# 1. USAR TU LLAVE REAL
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    st.success("✅ API Key cargada correctamente de los Secrets.")
else:
    st.error("❌ No se encontró la API Key.")
    st.stop()

# 2. BOTÓN PARA INICIAR EL ESCANEO
if st.button("🔍 Listar Modelos Disponibles"):
    try:
        st.write("---")
        st.write("### Resultados del Servidor de Google:")
        
        modelos_encontrados = []
        # Ejecutamos la función que me pediste analizar
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                modelos_encontrados.append(m.name)
                st.write(f"✅ **Permitido:** `{m.name}`")
        
        if not modelos_encontrados:
            st.warning("⚠️ Google no devolvió ningún modelo con permiso de generación.")
        
        st.write("---")
        st.info("Si los nombres empiezan con 'models/', esa es la ruta que debemos usar.")

    except Exception as e:
        st.error(f"❌ Error al intentar listar: {e}")
        st.write("Este error suele dar la pista final sobre la versión (v1 vs v1beta).")
