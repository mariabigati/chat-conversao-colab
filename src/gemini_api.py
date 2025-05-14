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
    # Usa Gemini para traduzir
    try:
        response = modelo.generate_content(f"Traduza para o inglês: '{prompt_pt}'")
        texto_traduzido = ""
        for part in response.parts:
            if hasattr(part, "text"):
                texto_traduzido += part.text.strip()
        return texto_traduzido
    except Exception as e:
        st.error(f"Erro ao traduzir o prompt: {e}")
        return prompt_pt  # Retorna o original como fallback
    
def gerar_imagem(prompt):
    prompt_en = traduzir_prompt(prompt)
    st.write("🔤 Prompt traduzido:", prompt_en)  # Para debug

    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {
        "authorization": f"Bearer {STABILITY_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "text_prompts": [{"text": prompt_en}],
        "cfg_scale": 7,
        "height": 512,
        "width": 512,
        "samples": 1,
        "steps": 30,
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            resposta_json = response.json()
            imagem_url = resposta_json["artifacts"][0]["url"]

            # Baixa a imagem
            imagem_response = requests.get(imagem_url)
            if imagem_response.status_code == 200:
                return Image.open(BytesIO(imagem_response.content))
            else:
                st.error(f"Erro ao baixar imagem: {imagem_response.status_code}")
                return None
        else:
            st.error(f"Erro {response.status_code}: {response.text}")
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
