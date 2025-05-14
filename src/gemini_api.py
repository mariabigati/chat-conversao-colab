import os
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from google.generativeai import types

# ========================
# CONFIGURAÇÃO DAS CHAVES
# ========================

# Stability API Key
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
if not STABILITY_API_KEY:
    st.error("⚠️ A chave da Stability AI (STABILITY_API_KEY) não foi encontrada.")
    st.stop()

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("⚠️ A chave da API Gemini (GEMINI_API_KEY) não foi encontrada.")
    st.stop()

# Configura Gemini
genai.configure(api_key=GEMINI_API_KEY)
modelo = genai.GenerativeModel(model_name="gemini-2.0-flash-exp-image-generation")

# ====================================
# FUNÇÃO PARA GERAR IMAGEM (Stability)
# ====================================
def traduzir_prompt(prompt_pt):
    try:
        prompt_gemini = f"Traduza para o inglês, apenas o texto traduzido, sem comentários extras: '{prompt_pt}'"
        response = modelo.generate_content(prompt_gemini)
        
        if hasattr(response, 'text'):
            return response.text.strip()
        else:
            texto_traduzido = ""
            for part in getattr(response, "parts", []):
                if hasattr(part, "text"):
                    texto_traduzido += part.text.strip()
            return texto_traduzido or prompt_pt  # fallback
    except Exception as e:
        st.error(f"Erro ao traduzir o prompt: {e}")
        return prompt_pt
    
def gerar_imagem(prompt):
    prompt_en = traduzir_prompt(prompt)

    url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "accept": "image/*",
    }
    data = {
        "prompt": prompt_en,
        "output_format": "png",
    }

    try:
        response = requests.post(url, headers=headers, files={"none": ''}, data=data)

        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            st.error(f"Erro {response.status_code}: {response.json()}")
            return None

    except Exception as e:
        st.error(f"Erro ao gerar imagem com Stability: {e}")
        return None

# ===================================
# FUNÇÃO PARA GERAR TEXTO (Gemini AI)
# ===================================
def gerar_conteudo(prompt: str, formato: str):
    if formato == "Imagem":
        imagem = gerar_imagem(prompt)
        return "", imagem

    # Para textos
    prompt_com_formato = f"Escreva um {formato.lower()} sobre o seguinte tema: {prompt}"

    try:
        generation_config = types.GenerationConfig(temperature=0.7)
        response = modelo.generate_content(prompt_com_formato, generation_config=generation_config)

        texto = ""
        for part in response.parts:
            if hasattr(part, "text"):
                texto += part.text.strip()

        return texto, None

    except Exception as e:
        st.error(f"Erro ao gerar conteúdo com Gemini: {e}")
        return None, None
