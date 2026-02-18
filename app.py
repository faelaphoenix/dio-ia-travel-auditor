import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrega as chaves do ambiente
load_dotenv()

# --- CAMADA DE TESTES E GOVERNANÇA ---
def system_health_check():
    """Valida se as chaves da Azure estão presentes antes de iniciar."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    if not endpoint or not key:
        return False, "🚨 Configuração ausente: Verifique as chaves AZURE_ENDPOINT e AZURE_KEY."
    return True, "✅ Conexão Azure: OK"

# --- CAMADA DE INTELIGÊNCIA (Com Redundância) ---
def analyze_document(image_file, model_type="prebuilt-receipt"):
    """Envia o documento para a Azure usando o modelo especificado."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    # Reposiciona o ponteiro do arquivo para garantir leitura múltipla se necessário
    image_file.seek(0)
    
    poller = client.begin_analyze_document(
        model_type, 
        analyze_request=image_file, 
        content_type="application/octet-stream"
    )
    return poller.result()

def check_compliance(result):
    """Aplica as regras de negócio: Teto R$ 80 e Filtro de Álcool."""
    violations = []
    total_value = 0.0
    found_total = False
    
    # Lista de Auditoria: Itens Proibidos
    prohibited_items = ["cerveja", "chopp", "vinho", "caipirinha", "vodka", "whisky", "margarita", "bebida alcoolica", "beer", "wine", "alcohol", "lata"]

    for doc in result.documents:
        # 1. Extração do Valor Total (Busca em múltiplos campos possíveis)
        total_field = doc.fields.get("Total") or doc.fields.get("TotalAmount") or doc.fields.get("AmountDue")
        
        if total_field and total_field.value_number is not None:
            total_value = total_field.value_number
            if total_value > 0:
                found_total = True
                if total_value > 80.0:
                    violations.append(f"⚠️ Alerta Financeiro: Gasto de R$ {total_value:.2f} excede o teto de R$ 80,00.")
        
        # 2. Auditoria de Itens (Filtro de Fraudes)
        if doc.fields.get("Items"):
            for item in doc.fields.get("Items").value_array:
                description_field = item.value_object.get("Description") or item.value_object.get("Content")
                item_description = description_field.value_string.lower() if description_field else ""
                
                for forbidden in prohibited_items:
                    if forbidden in item_description:
                        violations.append(f"🚫 Violação de Compliance: Item proibido -> '{item_description}'.")

    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- INTERFACE (STREAMLIT) ---
st.set_page_config(page_title="AI Travel Auditor", page_icon="🛡️")

st.title("🛡️ AI Travel Auditor")
st.markdown("### Auditoria Inteligente e Compliance (Padrão Nota Fiscal BR)")

# Check de Saúde na Sidebar
is_healthy, health_msg = system_health_check()
if not is_healthy:
    st.error(health_msg)
    st.stop()
st.sidebar.success(health_msg)

uploaded_file = st.file_uploader("Subir Cupom ou Nota Fiscal (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Iniciando Auditoria Multinível...'):
        try:
            # PASSO 1: Tenta como Recibo Genérico
            result = analyze_document(uploaded_file, "prebuilt-receipt")
            compliant, total, errors = check_compliance(result)

            # PASSO 2: Se o valor for 0 ou não encontrado, tenta como Invoice (Nota Fiscal)
            if total <= 0:
                st.sidebar.warning("🔄 Recibo complexo detectado. Acionando modelo de Nota Fiscal...")
                result = analyze_document(uploaded_file, "prebuilt-invoice")
                compliant, total, errors = check_compliance(result)

            st.divider()
            
            if compliant:
                st.success(f"✅ RECIBO APROVADO! Valor Identificado: R$ {total:.2f}")
                st.balloons()
            else:
                st.error("❌ RECIBO REPROVADO")
                if not errors and total == 0:
                    st.warning("🚨 Não foi possível extrair dados financeiros deste documento. Verifique a imagem.")
                for error in errors:
                    st.warning(error)
                st.info(f"Valor Final Processado: R$ {total:.2f}")

        except Exception as e:
            st.error(f"🚨 Falha Técnica: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("**Regras de Negócio:**")
st.sidebar.write("✅ Limite: R$ 80,00")
st.sidebar.write("✅ Tolerância Zero:
