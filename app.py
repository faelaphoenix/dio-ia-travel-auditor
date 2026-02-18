import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrego as variáveis de ambiente para garantir a segurança das credenciais
load_dotenv()

# Nome do modelo que treinei no Studio - Garanto que o nome esteja idêntico
CUSTOM_MODEL_ID = "travel-auditor" 

def system_health_check():
    """Valido se as chaves de conexão com a Azure estão configuradas corretamente."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    if not endpoint or not key:
        return False, "🚨 Configuração ausente: Verifique AZURE_ENDPOINT e AZURE_KEY."
    return True, "✅ Conexão Azure estabelecida."

def analyze_document(image_file, model_id):
    """Executo a chamada para a API da Azure utilizando o modelo de IA solicitado."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    client = DocumentIntelligenceClient(endpoint, AzureKeyCredential(key))
    
    # Reseto o ponteiro do arquivo para permitir múltiplas leituras na cascata de fallback
    image_file.seek(0)
    
    poller = client.begin_analyze_document(
        model_id, 
        analyze_request=image_file, 
        content_type="application/octet-stream"
    )
    return poller.result()

def check_compliance(result):
    """Eu realizo uma varredura profunda para garantir que nenhum dado financeiro ou item proibido seja ignorado."""
    violations = []
    total_value = 0.0
    found_total = False
    
    # Minha lista de auditoria estrita para itens não reembolsáveis
    prohibited_items = ["cerveja", "chopp", "vinho", "vodka", "whisky", "caipirinha", "beer", "wine", "alcohol", "cocktail"]

    for doc in result.documents:
        fields = doc.fields
        
        # 1. MAPEAMENTO DE VALOR TOTAL
        total_field = fields.get("Total") or fields.get("TotalAmount") or fields.get("AmountDue") or fields.get("TotalValue")
        
        if total_field:
            if total_field.value_number is not None:
                total_value = total_field.value_number
            elif hasattr(total_field, 'value_currency') and total_field.value_currency:
                total_value = total_field.value_currency.amount
            
            if total_value > 0:
                found_total = True
                if total_value > 80.0:
                    violations.append(f"⚠️ Alerta Compliance: Valor R$ {total_value:.2f} excede o teto de R$ 80,00.")
        
        # 2. AUDITORIA DE ITENS (Lógica Reforçada)
        items_field = fields.get("Items")
        if items_field and items_field.value_array:
            for item in items_field.value_array:
                item_text = ""
                
                # Caso A: Modelo Prebuilt (Estrutura de objeto complexo)
                if hasattr(item, 'value_object') and item.value_object:
                    # Tento capturar a descrição em qualquer campo possível do objeto
                    desc_field = (item.value_object.get("Description") or 
                                 item.value_object.get("Content") or 
                                 item.value_object.get("ProductCode"))
                    if desc_field:
                        item_text = desc_field.value_string.lower() if desc_field.value_string else ""
                
                # Caso B: Modelo Custom ou Fallback simples
                elif hasattr(item, 'value_string') and item.value_string:
                    item_text = item.value_string.lower()
                
                # Verifico se o texto capturado contém algum item proibido
                if item_text:
                    for forbidden in prohibited_items:
                        if forbidden in item_text:
                            violations.append(f"🚫 Violação: Item proibido detectado -> '{item_text.title()}'.")

    # Retorno o veredito final
    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- Interface Streamlit ---
st.set_page_config(page_title="Auditor de Viagens IA", page_icon="🛡️")

st.title("🛡️ AI Travel Auditor")
st.markdown(f"**Governança:** Auditoria Híbrida e Compliance em Tempo Real")

is_healthy, health_msg = system_health_check()
if not is_healthy:
    st.error(health_msg)
    st.stop()

uploaded_file = st.file_uploader("Subir Recibo para Auditoria", type=["jpg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Auditando documento e verificando compliance...'):
        try:
            total = 0
            result = None
            
            # PASSO 1: Modelo Customizado (Especialista)
            try:
                result = analyze_document(uploaded_file, CUSTOM_MODEL_ID)
                compliant, total, errors = check_compliance(result)
            except Exception:
                st.sidebar.info(f"ℹ️ Custom Model '{CUSTOM_MODEL_ID}' indisponível.")

            # PASSO 2: Modelo Geral de Recibos
            if total <= 0:
                st.sidebar.warning("🔄 Recorrendo ao modelo Prebuilt Receipts...")
                result = analyze_document(uploaded_file, "prebuilt-receipt")
                compliant, total, errors = check_compliance(result)

            # PASSO 3: Modelo de Faturas (Invoices)
            if total <= 0:
                st.sidebar.warning("🔄 Recorrendo ao modelo Prebuilt Invoices...")
                result = analyze_document(uploaded_file, "prebuilt-invoice")
                compliant, total, errors = check_compliance(result)

            st.divider()
            
            if total > 0:
                if compliant:
                    st.success(f"✅ RECIBO APROVADO! Total: R$ {total:.2f}")
                    st.balloons()
                else:
                    st.error("❌ RECIBO REPROVADO")
                    for error in errors:
                        st.warning(error)
            else:
                st.error("❌ FALHA NA EXTRAÇÃO: Dados financeiros não identificados.")

        except Exception as e:
            if "429" in str(e):
                st.error("⚠️ Cota F0 atingida. Aguarde 60 segundos.")
            else:
                st.error(f"🚨 Erro técnico inesperado: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.info("Governança Corporativa: Teto R$ 80 | Zero Álcool")



