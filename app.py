import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrega as chaves do ambiente
load_dotenv()

# --- CAMADA DE TESTES E GOVERNANÇA (Boa Prática Sênior) ---
def system_health_check():
    """Valida se todas as chaves e conexões estão prontas para o uso."""
    checks = {
        "AZURE_ENDPOINT": os.getenv("AZURE_ENDPOINT"),
        "AZURE_KEY": os.getenv("AZURE_KEY")
    }
    
    missing = [k for k, v in checks.items() if not v]
    if missing:
        return False, f"🚨 Erro de Configuração: Faltam as chaves {', '.join(missing)} no ambiente."
    
    return True, "✅ Sistema Operacional"

# --- CAMADA DE INTELIGÊNCIA ---
def analyze_receipt(image_file):
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")

    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    # Processamento com o modelo de recibos da Azure
    poller = client.begin_analyze_document(
        "prebuilt-receipt", 
        analyze_request=image_file, 
        content_type="application/octet-stream"
    )
    return poller.result()

def check_compliance(result):
    violations = []
    total_value = 0.0
    found_total = False
    
    # Lista de Auditoria: Palavras proibidas (Política de Álcool)
    prohibited_items = ["cerveja", "chopp", "vinho", "caipirinha", "vodka", "whisky", "margarita", "bebida alcoolica", "beer", "wine", "alcohol"]

    for receipt in result.documents:
        # 1. Validação do Campo Total
        total_field = receipt.fields.get("Total")
        if total_field and total_field.value_number is not None:
            total_value = total_field.value_number
            found_total = True
            if total_value > 80.0:
                violations.append(f"⚠️ Alerta Financeiro: Gasto de R$ {total_value:.2f} excede o teto de R$ 80,00.")
        else:
            violations.append("🚨 Erro de Dados: Não foi possível localizar o valor total no documento.")

        # 2. Auditoria de Itens (Filtro de Fraudes/Políticas)
        if receipt.fields.get("Items"):
            for item in receipt.fields.get("Items").value_array:
                description_field = item.value_object.get("Description")
                item_description = description_field.value_string.lower() if description_field else ""
                
                for forbidden in prohibited_items:
                    if forbidden in item_description:
                        violations.append(f"🚫 Violação de Compliance: Item proibido detectado -> '{item_description}'.")

    # Aprovação final exige: Zero violações E valor total identificado
    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- INTERFACE (STREAMLIT) ---
st.set_page_config(page_title="AI Travel Auditor", page_icon="🛡️", layout="centered")

st.title("🛡️ AI Travel Auditor")
st.markdown("### Auditoria Inteligente e Compliance de Viagens")
st.sidebar.header("Configurações de Auditoria")

# Executa teste de saúde antes de liberar o upload
is_healthy, health_msg = system_health_check()

if not is_healthy:
    st.error(health_msg)
    st.stop() # Interrompe a execução se os testes falharem
else:
    st.sidebar.success(health_msg)

uploaded_file = st.file_uploader("Subir recibo para análise (JPG, PNG, PDF)", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Auditando documento com Azure AI...'):
        try:
            # 1. Análise da IA
            analysis_result = analyze_receipt(uploaded_file)
            
            # 2. Verificação de Regras de Negócio
            compliant, total, errors = check_compliance(analysis_result)

            st.divider()
            
            if compliant:
                st.success(f"✅ RECIBO APROVADO! Valor: R$ {total:.2f}")
                st.balloons()
            else:
                st.error("❌ RECIBO REPROVADO")
                for error in errors:
                    st.warning(error)
                st.info(f"Valor extraído: R$ {total:.2f}")

        except Exception as e:
            st.error(f"🚨 Falha Crítica no Processamento: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("📌 **Teto:** R$ 80,00")
st.sidebar.write("📌 **Política:** Proibido Álcool")


