import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrega as chaves do seu arquivo .env protegido
load_dotenv()

def analyze_receipt(image_file):
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")

    # Configuração do Cliente Azure
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    # Processamento do documento (modelo pré-treinado de recibos)
    poller = client.begin_analyze_document("prebuilt-receipt", analyze_request=image_file, content_type="application/octet-stream")
    result = poller.result()
    
    return result

def check_compliance(result):
    violations = []
    total_value = 0.0
    is_compliant = True
    
    # Palavras-chave proibidas (Governança de Bebidas Alcoólicas)
    prohibited_items = ["cerveja", "chopp", "vinho", "caipirinha", "vodka", "whisky", "margarita", "bebida alcoolica"]

    for receipt in result.documents:
        # 1. Validação de Valor Teto (R$ 80,00)
        if receipt.fields.get("Total"):
            total_value = receipt.fields.get("Total").value_number
            if total_value > 80.0:
                violations.append(f"⚠️ Valor total (R$ {total_value:.2f}) excede o limite de R$ 80,00.")
                is_compliant = False

        # 2. Busca por Itens Proibidos
        if receipt.fields.get("Items"):
            for item in receipt.fields.get("Items").value_array:
                item_description = item.value_object.get("Description").value_string.lower() if item.value_object.get("Description") else ""
                
                for forbidden in prohibited_items:
                    if forbidden in item_description:
                        violations.append(f"🚨 Item proibido detectado: {item_description}")
                        is_compliant = False

    return is_compliant, total_value, violations

# --- Interface Streamlit ---
st.set_page_config(page_title="AI Travel Auditor", page_icon="🛡️")
st.title("🛡️ AI Travel Auditor")
st.subheader("Auditoria Inteligente de Recibos de Viagem")

uploaded_file = st.file_uploader("Selecione a foto de um recibo para auditoria", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    with st.spinner('Analisando conformidade com IA Azure...'):
        try:
            # Chama a análise
            analysis_result = analyze_receipt(uploaded_file)
            compliant, total, errors = check_compliance(analysis_result)

            st.divider()
            
            if compliant:
                st.success(f"✅ Recibo Aprovado! Valor Total: R$ {total:.2f}")
                st.balloons()
            else:
                st.error(f"❌ Recibo Reprovado pela Auditoria")
                for error in errors:
                    st.warning(error)
                st.info(f"Valor Total Identificado: R$ {total:.2f}")

        except Exception as e:
            st.error(f"Erro na análise técnica: {e}")

st.sidebar.info("Desenvolvido para conformidade corporativa utilizando Azure AI.")

