import streamlit as st
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("A chave da API não foi encontrada. Verifique seu arquivo .env.")
    st.stop()

# Importações das funções Gemini
from gemini_api import gerar_conteudo, gerar_imagem

# Iniciar lista de mensagens persistente
if "mensagens" not in st.session_state:
    st.session_state["mensagens"] = []

# Estilo da interface
st.markdown(
    """
    <style>
     header {
            background-color: rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(6px) !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3) !important;
        }
    .stApp {
        background-image: url('https://cdna.artstation.com/p/assets/images/images/007/479/712/large/tzu-yu-kao-at-pastel-night-sky-0925ss1.jpg?1506426552');  /* Imagem de fundo etérea de estrelas */
        background-size: cover;
        background-position: center;
        color: #fff;
        font-family: 'Courier New', Courier, monospace;
    }
    .stTextInput, .stTextArea {
        background-color: rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(6px) !important;
        border-radius: 10px;
        padding: 10px;
        color: #2e3a59;
    }
    .stButton>button {
        background-color: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(6px) !important;
        color: white;
        border-radius: 50px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #1d53db;
    }
    .stSelectbox select {
        background-color: rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(6px) !important;
        border-radius: 10px;
        padding: 10px;
        color: #2e3a59;
    }
    h1 {
        font-size: 3em;
        color: #f4f7fc;
        text-align: center;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stSpinner {
        color: #fff;
    }
    .conteudo-gerado {
        background-color: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(6px);
        color: #f4f7fc;
        text-align: center;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-radius: 20px;
    
    </style>
    """, unsafe_allow_html=True
)

# Interface principal
st.title("Gerador de Texto & Imagem")

st.markdown('<div class="cloud-layer"></div>', unsafe_allow_html=True)

with st.container():
    st.markdown(
        """
        <div class="fixed-input">
        """, unsafe_allow_html=True
    )

    prompt = st.text_area("Digite seu prompt:", key="prompt_input")
    formato = st.selectbox("Formato de saída:", ["Poema", "Artigo", "Resumo", "Imagem"], key="formato_select")
    gerar = st.button("Gerar", key="gerar_botao")

    st.markdown("</div>", unsafe_allow_html=True)

if gerar:
    with st.spinner("Gerando com as estrelas..."):
        texto, imagem = gerar_conteudo(prompt, formato)

        nova_mensagem = {
            "prompt": prompt,
            "formato": formato,
            "texto": texto,
            "imagem": imagem
        }

        st.session_state.mensagens.append(nova_mensagem)

# Mostrar todas as mensagens empilhadas
for msg in st.session_state.mensagens:
    conteudo_html = f"""
    <div class="conteudo-gerado">
        <p><strong>Prompt:</strong> {msg['prompt']}</p>
        <p><strong>Formato:</strong> {msg['formato']}</p>
    """

    if msg["formato"] == "Imagem" and msg["imagem"]:
        conteudo_html += f'<img src="{msg["imagem"]}" style="max-width:100%; border-radius:10px;" alt="Imagem gerada"/>'
    elif msg["texto"]:
        conteudo_html += f"<div>{msg['texto']}</div>"
    else:
        conteudo_html += "<div><em>Nada foi gerado.</em></div>"

    conteudo_html += "</div>"

    st.markdown(conteudo_html, unsafe_allow_html=True)
    
    st.markdown("---")
