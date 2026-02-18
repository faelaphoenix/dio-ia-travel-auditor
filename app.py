import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrega as chaves do ambiente
load_dotenv()

# --- CONFIGURAÇÃO DE GOVERNANÇA ---
# Nome do modelo que aparece no meu Studio
CUSTOM_MODEL_ID = "travel-auditor" 

def system_health_check():
    """Valida se as chaves da Azure estão presentes."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    if not endpoint or not key:
        return False, "🚨 Configuração ausente nos Secrets!"
    return True, "✅ Conexão Azure: Ativa"

def analyze_document(image_file, model_id):
    """Analisa o documento usando o modelo especificado."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    image_file.seek(0)
    
    poller = client.begin_analyze_document(
        model_id, 
        analyze_request=image_file, 
        content_type="application/octet-stream"
    )
    return poller.result()

def check_compliance(result):
    """Regras de Negócio: Teto R$ 80 e Proibição de Álcool."""
    violations = []
    total_value = 0.0
    found_total = False
    
    # Filtro de Compliance (Termos Proibidos)
    prohibited_items = ["cerveja", "chopp", "vinho", "vodka", "beer", "wine", "alcohol", "whisky"]

    for doc in result.documents:
        # Extração de Valor Total (Suporta campos Custom e Prebuilt)
        total_field = doc.fields.get("Total") or doc.fields.get("TotalAmount")
        
        if total_field and total_field.value_number is not None:
            total_value = total_field.value_number
            if total_value > 0:
                found_total = True
                if total_value > 80.0:
                    violations.append(f"⚠️ Alerta: Valor R$ {total_value:.2f} excede o teto de R$ 80,00.")
        
        # Auditoria de Itens
        if doc.fields.get("Items"):
            items_list = doc.fields.get("Items").value_array
            for item in items_list:
                # Trata diferentes estruturas de retorno (Objeto ou String)
                if hasattr(item, 'value_object'):
                    desc_obj = item.value_object.get("Description") or item.value_object.get("Content")
                    desc = desc_obj.value_string.lower() if desc_obj else ""
                else:
                    desc = str(item.value_string if hasattr(item, 'value_string') else item).lower()
                
                for forbidden in prohibited_items:
                    if forbidden in desc:
                        violations.append(f"🚫 Item Proibido: '{desc}' detectado.")

    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="AI Travel Auditor Hybrid", page_icon="🛡️")

st.title("🛡️ AI Travel Auditor")
st.markdown(f"**Estratégia:** Custom (`{CUSTOM_MODEL_ID}`) + Fallback (Prebuilt)")

is_healthy, health_msg = system_health_check()
if not is_healthy:
    st.error(health_msg)
    st.stop()

uploaded_file = st.file_uploader("Subir Recibo para Auditoria", type=["jpg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Iniciando auditoria inteligente...'):
        try:
            # PASSO 1: Tenta o meu modelo Especialista (Custom)
            result = analyze_document(uploaded_file, CUSTOM_MODEL_ID)
            compliant, total, errors = check_compliance(result)

            # PASSO 2: Se falhar em achar o valor, tenta o modelo Geral (Fallback)
            if total <= 0:
                st.sidebar.warning("🔄 Modelo customizado inconclusivo. Acionando base geral...")
                result = analyze_document(uploaded_file, "prebuilt-receipt")
                compliant, total, errors = check_compliance(result)

            st.divider()
            
            if compliant:
                st.success(f"✅ RECIBO APROVADO! Valor: R$ {total:.2f}")
                st.balloons()
            else:
                st.error("❌ RECIBO REPROVADO")
                for error in errors:
                    st.warning(error)
                if total == 0:
                    st.info("💡 Nota: A IA não conseguiu extrair dados financeiros deste documento.")

        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ Cota F0 Excedida. Aguarde 1 minuto para o próximo teste.")
            else:
                st.error(f"🚨 Erro técnico: {str(e)}")

st.sidebar.info("Governança: Teto R$ 80 | Zero Álcool")

