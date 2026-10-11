import os
import time
import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Configuração da página visual
st.set_page_config(page_title="Redação Passo a Passo", page_icon="📝")
st.title("📝 Redação Passo a Passo")
st.caption("Construa sua redação do ENEM frase por frase com apoio de IA.")

# 2. Verificação da Chave de API
if not os.environ.get("GEMINI_API_KEY"):
    st.error("⚠️ A chave GEMINI_API_KEY não foi configurada no terminal!")
    st.info("No terminal, execute: set GEMINI_API_KEY=sua_chave (Windows) ou export GEMINI_API_KEY=sua_chave (Mac/Linux).")
    st.stop()

SYSTEM_INSTRUCTION = """
Você é o assistente pedagógico "Redação Passo a Passo".
Sua missão é ensinar o aluno a escrever uma redação para o ENEM FRASE POR FRASE.
Nunca escreva o texto por ele. Valide a frase atual, corrija pequenos erros gramaticais
e peça explicitamente a próxima frase da estrutura.
"""

# 3. Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu tutor de redação do ENEM. Qual tema você gostaria de treinar hoje?"}
    ]

# 4. Exibe o histórico de conversa
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 5. Entrada do usuário
if prompt := st.chat_input("Digite o tema ou sua frase aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando sua frase..."):
            client = genai.Client()

            # Formata o histórico
            formatted_history = []
            for msg in st.session_state.messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                formatted_history.append(
                    types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg["content"])]
                    )
                )

            chat = client.chats.create(
                model="gemini-3.8-flash",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3
                ),
                history=formatted_history
            )

            # Sistema de tentativas automáticas em caso de erro 503
            max_tentativas = 3
            sucesso = False

            for tentativa in range(max_tentativas):
                try:
                    resposta = chat.send_message(prompt)
                    st.write(resposta.text)
                    st.session_state.messages.append({"role": "assistant", "content": resposta.text})
                    sucesso = True
                    break
                except APIError as e:
                    if e.code == 503 and tentativa < max_tentativas - 1:
                        time.sleep(2)  # Espera 2 segundos antes de tentar de novo
                        continue
                    else:
                        st.error(" O servidor da IA está temporariamente sobrecarregado (Erro 503). Por favor, tente enviar novamente em alguns instantes.")
                        break
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
                    break