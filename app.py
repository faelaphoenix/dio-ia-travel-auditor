import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrega as chaves do ambiente
load_dotenv()

# --- CAMADA DE TESTES E GOVERNANÇA ---
def system_health_check():
    """Valida se as chaves da Azure estão presentes."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    if not endpoint or not key:
        return False, "🚨 Erro: Verifique as chaves AZURE_ENDPOINT e AZURE_KEY no Secrets."
    return True, "✅ Conexão Azure: OK"

# --- CAMADA DE INTELIGÊNCIA ---
def analyze_document(image_file, model_type="prebuilt-receipt"):
    """Processa o documento na Azure."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    image_file.seek(0) # Reseta o ponteiro para leitura
    
    poller = client.begin_analyze_document(
        model_type, 
        analyze_request=image_file, 
        content_type="application/octet-stream"
    )
    return poller.result()

def check_compliance(result):
    """Aplica regras de teto de R$ 80 e proibição de álcool."""
    violations = []
    total_value = 0.0
    found_total = False
    
    # Lista de Auditoria
    prohibited_items = ["cerveja", "chopp", "vinho", "caipirinha", "vodka", "whisky", "beer", "wine", "alcohol"]

    for doc in result.documents:
        # Busca flexível pelo valor total (comum em notas BR)
        fields = doc.fields
        total_field = fields.get("Total") or fields.get("TotalAmount") or fields.get("AmountDue")
        
        if total_field and total_field.value_number is not None:
            total_value = total_field.value_number
            if total_value > 0:
                found_total = True
                if total_value > 80.0:
                    violations.append(f"⚠️ Excede teto: R$ {total_value:.2f} (Limite: R$ 80,00)")
        
        # Auditoria de Itens
        if fields.get("Items"):
            for item in fields.get("Items").value_array:
                item_data = item.value_object
                desc = item_data.get("Description") or item_data.get("Content")
                item_text = desc.value_string.lower() if desc else ""
                
                for forbidden in prohibited_items:
                    if forbidden in item_text:
                        violations.append(f"🚫 Item proibido: '{item_text}'")

    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- INTERFACE ---
st.set_page_config(page_title="AI Travel Auditor", page_icon="🛡️")

st.title("🛡️ AI Travel Auditor")
st.markdown("### Auditoria Inteligente e Compliance")

is_healthy, health_msg = system_health_check()
if not is_healthy:
    st.error(health_msg)
    st.stop()

st.sidebar.success(health_msg)
uploaded_file = st.file_uploader("Subir Cupom ou Nota Fiscal", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Auditando documento...'):
        try:
            # Estratégia Multinível: Tenta Recibo, se falhar tenta Fatura
            result = analyze_document(uploaded_file, "prebuilt-receipt")
            compliant, total, errors = check_compliance(result)

            if total <= 0:
                st.sidebar.warning("🔄 Refinando análise como Nota Fiscal...")
                result = analyze_document(uploaded_file, "prebuilt-invoice")
                compliant, total, errors = check_compliance(result)

            st.divider()
            
            if compliant:
                st.success(f"✅ APROVADO! Valor: R$ {total:.2f}")
                st.balloons()
            else:
                st.error("❌ REPROVADO")
                if not errors and total == 0:
                    st.warning("🚨 Não foi possível identificar valores financeiros.")
                for error in errors:
                    st.warning(error)
                st.info(f"Valor extraído: R$ {total:.2f}")

        except Exception as e:
            st.error(f"🚨 Erro técnico: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("✅ Limite: R$ 80,00")
st.sidebar.write("✅ Tolerância Zero: Álcool")
