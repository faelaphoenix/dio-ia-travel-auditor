import streamlit as st
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
import os
from dotenv import load_dotenv

# Carrego as variáveis de ambiente para garantir a segurança das credenciais
load_dotenv()

# Defino o ID do modelo que treinei no Document Intelligence Studio para notas específicas
CUSTOM_MODEL_ID = "travel-auditor" 

def system_health_check():
    """Valido se as chaves de conexão com a Azure estão configuradas corretamente."""
    endpoint = os.getenv("AZURE_ENDPOINT")
    key = os.getenv("AZURE_KEY")
    if not endpoint or not key:
        return False, "🚨 Configuração ausente: Verifique AZURE_ENDPOINT e AZURE_KEY."
    return True, "✅ Conexão Azure estabelecida com sucesso."

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
    """Aplico as regras de governança: Teto de R$ 80 e proibição estrita de álcool."""
    violations = []
    total_value = 0.0
    found_total = False
    
    # Lista de termos que ferem a política de reembolso da empresa
    prohibited_items = ["cerveja", "chopp", "vinho", "vodka", "whisky", "caipirinha", "beer", "wine", "alcohol"]

    for doc in result.documents:
        # Busco o valor total tentando mapear campos de modelos Custom e Prebuilt
        total_field = doc.fields.get("Total") or doc.fields.get("TotalAmount")
        
        if total_field and total_field.value_number is not None:
            total_value = total_field.value_number
            if total_value > 0:
                found_total = True
                # Regra de negócio: Limite de despesa
                if total_value > 80.0:
                    violations.append(f"⚠️ Alerta: Valor R$ {total_value:.2f} excede o teto permitido de R$ 80,00.")
        
        # Realizo a varredura de itens para identificar possíveis fraudes ou itens não reembolsáveis
        if doc.fields.get("Items"):
            items_list = doc.fields.get("Items").value_array
            for item in items_list:
                # Trato a descrição do item independente da estrutura de retorno do modelo
                if hasattr(item, 'value_object'):
                    desc_obj = item.value_object.get("Description") or item.value_object.get("Content")
                    desc = desc_obj.value_string.lower() if desc_obj else ""
                else:
                    desc = str(item.value_string if hasattr(item, 'value_string') else item).lower()
                
                for forbidden in prohibited_items:
                    if forbidden in desc:
                        violations.append(f"🚫 Violação de Compliance: Item proibido detectado -> '{desc}'.")

    # O recibo só é complacente se não houver violações e o valor total for identificado
    is_compliant = len(violations) == 0 and found_total
    return is_compliant, total_value, violations

# --- Interface de Usuário (Streamlit) ---
st.set_page_config(page_title="Auditor de Viagens IA", page_icon="🛡️")

st.title("🛡️ AI Travel Auditor")
st.markdown(f"**Arquitetura:** Cascata de Fallback (Custom + Receipts + Invoices)")

# Valido a saúde do sistema antes de permitir o upload
is_healthy, health_msg = system_health_check()
if not is_healthy:
    st.error(health_msg)
    st.stop()

uploaded_file = st.file_uploader("Faça o upload do recibo (JPG, PNG ou PDF)", type=["jpg", "png", "pdf"])

if uploaded_file:
    with st.spinner('Processando auditoria multinível...'):
        try:
            total = 0
            result = None
            
            # TENTATIVA 1: Utilizo meu modelo customizado, treinado para layouts específicos
            try:
                result = analyze_document(uploaded_file, CUSTOM_MODEL_ID)
                compliant, total, errors = check_compliance(result)
            except Exception:
                # Caso o modelo customizado esteja offline ou em treino, registro e sigo o fluxo
                st.sidebar.info(f"⏳ Modelo '{CUSTOM_MODEL_ID}' indisponível. Acionando contingência.")

            # TENTATIVA 2: Se o valor não foi capturado, recorro ao modelo geral de Recibos
            if total <= 0:
                st.sidebar.warning("🔄 Analisando via modelo genérico (Prebuilt Receipts).")
                result = analyze_document(uploaded_file, "prebuilt-receipt")
                compliant, total, errors = check_compliance(result)

            # TENTATIVA 3: Último recurso - utilizo o modelo de Invoices para notas fiscais complexas
            if total <= 0:
                st.sidebar.warning("🔄 Analisando via modelo de Notas Fiscais (Invoices).")
                result = analyze_document(uploaded_file, "prebuilt-invoice")
                compliant, total, errors = check_compliance(result)

            st.divider()
            
            # Exibo o veredito final baseado na análise da IA
            if total > 0:
                if compliant:
                    st.success(f"✅ RECIBO APROVADO! Valor extraído: R$ {total:.2f}")
                    st.balloons()
                else:
                    st.error("❌ RECIBO REPROVADO")
                    for error in errors:
                        st.warning(error)
            else:
                st.error("❌ ERRO DE LEITURA: Não foi possível identificar valores financeiros.")

        except Exception as e:
            # Gerenciamento de cota F0 da Azure
            if "429" in str(e):
                st.error("⚠️ Limite de requisições atingido (Cota F0). Aguarde 60 segundos.")
            else:
                st.error(f"🚨 Falha técnica no processamento: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("**Políticas de Auditoria:**")
st.sidebar.write("- Limite por recibo: R$ 80,00")
st.sidebar.write("- Restrição total de itens alcoólicos")


