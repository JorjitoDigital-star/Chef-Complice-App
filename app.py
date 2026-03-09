import google.generativeai as genai

genai.configure(api_key="TU_API_KEY")

try:
    print("Modelos disponibles para tu cuenta:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error al listar: {e}")
