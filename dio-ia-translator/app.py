import streamlit as st
import os
from docx import Document
from PyPDF2 import PdfReader
from openai import AzureOpenAI

class LyricTranslator:
    def __init__(self):
        """
        Inicializa o cliente Azure OpenAI usando os segredos do Streamlit.
        As chaves devem estar no arquivo .streamlit/secrets.toml localmente
        ou configuradas no painel do Streamlit Cloud.
        """
        try:
            self.client = AzureOpenAI(
                azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
                api_key=st.secrets["AZURE_OPENAI_KEY"],
                api_version="2024-08-01-preview"
            )
        except Exception as e:
            st.error(f"Erro ao carregar credenciais: {e}")

    def extract_text(self, uploaded_file):
        """Extrai texto de arquivos PDF ou DOCX."""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        text = ""
        
        if file_extension == 'pdf':
            pdf_reader = PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file_extension == 'docx':
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        else:
            text = uploaded_file.read().decode("utf-8")
        return text

    def translate_and_analyze(self, text, target_language):
        """Realiza a tradução e a análise de 'vibe' da letra."""
        prompt = (
            f"Você é um tradutor especialista em música e analista cultural. "
            f"Traduza a seguinte letra para o idioma: {target_language}. "
            f"Após a tradução, adicione uma seção chamada '--- ANÁLISE DE VIBE ---' "
            f"descrevendo o sentimento, a energia e o tom emocional da letra original."
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erro na tradução: {str(e)}"

def main():
    st.set_page_config(page_title="Azure Lyric Translator", page_icon="🌐", layout="wide")
    
    st.title("🌐 Azure Universal Lyric Translator & Vibe Analyzer")
    st.markdown(f"**Dev:** Rafaela (UFV / Senior Governance Analyst) | **Stack:** Azure OpenAI")

    translator = LyricTranslator()

    # Sidebar para configurações
    st.sidebar.header("Configurações")
    target_lang = st.sidebar.selectbox(
        "Para qual idioma deseja traduzir?",
        ["Português", "Inglês", "Espanhol", "Francês", "Alemão", "Italiano"]
    )

    # Área de Upload
    uploaded_file = st.file_uploader("Suba a letra da música (TXT, PDF ou DOCX)", type=["txt", "pdf", "docx"])
    
    col1, col2 = st.columns(2)

    if uploaded_file is not None:
        raw_text = translator.extract_text(uploaded_file)
        
        with col1:
            st.subheader("Letra Original")
            st.text_area("Original", raw_text, height=400)

        if st.button("Traduzir e Analisar Vibe ✨"):
            with st.spinner("A IA está analisando a vibe e traduzindo..."):
                result = translator.translate_and_analyze(raw_text, target_lang)
                
                with col2:
                    st.subheader(f"Tradução ({target_lang}) & Vibe")
                    st.write(result)

if __name__ == "__main__":
    main()