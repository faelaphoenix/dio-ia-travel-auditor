import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

def initialize_audit_infrastructure():
    # Carrega as chaves do seu .env profissional
    load_dotenv()
    
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    
    print(f"🔍 Iniciando conexão com o storage: {container_name}...")
    
    try:
        # Estabelece conexão com o serviço de Blob
        service_client = BlobServiceClient.from_connection_string(connection_string)
        
        # Tenta criar o container (se já não existir)
        container_client = service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            print(f"✅ Sucesso! Container '{container_name}' criado para auditoria.")
        else:
            print(f"ℹ️ O container '{container_name}' já está pronto para uso.")
            
    except Exception as e:
        print(f"🚨 Falha de Governança: Não foi possível conectar. Verifique as chaves no .env.")
        print(f"Erro: {e}")

if __name__ == "__main__":
    initialize_audit_infrastructure()