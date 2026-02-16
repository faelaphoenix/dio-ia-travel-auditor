# 🌐 Azure Universal Lyric Translator & Vibe Analyzer

---
![Azure OpenAI](https://img.shields.io/badge/Azure_OpenAI-0072C6?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/python-3.10-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Paradigma](https://img.shields.io/badge/Paradigma-POO-blueviolet?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📝 Descrição do Projeto
Este projeto é um tradutor poliglota de letras de música que utiliza a stack de **IA Generativa da Microsoft Azure**. O diferencial desta solução é a camada de **Governança de Dados** e o módulo inovador de **Análise de Vibe (Sentimento)**, que interpreta o tom emocional da obra original.

> **Status do Projeto:** 🚀 [CLIQUE AQUI PARA TESTAR O APP AO VIVO](https://dio-ia-translator.streamlit.app/)

Desenvolvido como projeto final para o Bootcamp de IA da **DIO**, aplicando conceitos avançados de Programação Orientada a Objetos (POO) e Segurança da Informação.

## ✨ Funcionalidades
- **Tradução Multilíngue:** Suporta diversos idiomas utilizando o modelo `gpt-4o-mini`.
- **Análise de Vibe:** Identifica sentimento, energia e tom de voz da letra.
- **Processamento de Arquivos:** Suporte nativo para extração de texto de arquivos `.pdf` e `.docx`.
- **Filtro de Conteúdo (Content Safety):** Implementação de regras de governança para detectar e tratar conteúdos ofensivos ou sensíveis.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.10
- **IA:** Azure OpenAI Service (GPT-4o-mini)
- **Interface:** Streamlit
- **Extração de Dados:** PyPDF2 e python-docx
- **Cloud/Hospedagem:** Streamlit Community Cloud



## 🔒 Governança e Segurança
Como especialista em governança, este projeto foi construído seguindo as melhores práticas de **SecDevOps**:
- **Gestão de Segredos:** Utilização de `st.secrets` e variáveis de ambiente para impedir o vazamento de chaves de API.
- **Tratamento de Exceções:** Lógica robusta para capturar erros de política de conteúdo (Content Filter) do Azure.
- **Ambiente Isolado:** Desenvolvimento realizado em ambientes virtuais (Conda/Venv).

## 🚀 Como Rodar o Projeto
1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/dio-ia-translator.git](https://github.com/SEU_USUARIO/dio-ia-translator.git)