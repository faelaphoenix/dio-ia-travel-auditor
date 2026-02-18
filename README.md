🛡️ AI Travel Auditor: Inteligência Artificial na Governança de Despesas

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![MIT License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)

### 🔗 Acesse a aplicação em tempo real:
[![Abrir no Streamlit](https://static.streamlit.io/badges/streamlit_badge_svg)](https://antifraude-ai.streamlit.app/)

O **AI Travel Auditor** é uma solução de ponta que automatiza o processo de auditoria de recibos de viagem. Utilizando **Inteligência Artificial Documental**, o sistema garante o cumprimento das políticas corporativas, prevenindo fraudes financeiras e garantindo conformidade (compliance) em tempo real.

Bem-vindo ao **AI Travel Auditor**! Este projeto foi desenvolvido para automatizar o processo de auditoria de recibos de viagem, utilizando **Inteligência Artificial Documental** para garantir o cumprimento das políticas corporativas e prevenir fraudes financeiras.

---

## 📋 Sobre o Projeto

O objetivo deste sistema é analisar recibos de alimentação e transporte, extraindo dados críticos de forma automática e aplicando regras de negócio rigorosas para validar a conformidade dos gastos.

### 🚩 Regras de Auditoria Implementadas:
* **Teto de Gastos:** Identificação automática de despesas acima de **R$ 80,00**.
* **Itens Proibidos:** Detecção de compra de **bebidas alcoólicas** em recibos de refeição.
* **Integridade de Dados:** Extração de CNPJ, data e itens detalhados para cruzamento de informações.

---

## 🛠️ Tecnologias Utilizadas

Este projeto utiliza o estado da arte em serviços de nuvem e IA:

* **Azure AI Document Intelligence:** O motor de OCR e IA que interpreta os recibos.
* **Azure Blob Storage:** Armazenamento seguro e escalável das evidências (fotos dos recibos).
* **Python:** Linguagem base para a lógica de auditoria e integração.
* **Streamlit:** Interface web intuitiva para o usuário final.
* **Python-dotenv:** Gestão segura de chaves e variáveis de ambiente (Governança de Segredos).

---

## 🏗️ Arquitetura da Solução

[Image of an architecture diagram showing a user uploading a receipt to Streamlit, which is then processed by Azure AI Document Intelligence and stored in Azure Blob Storage]

A solução segue o fluxo:
1.  **Upload:** O auditor sobe a imagem do recibo via interface Streamlit.
2.  **Processamento:** O Azure Document Intelligence extrai os dados estruturados (JSON).
3.  **Análise:** O sistema Python valida o valor total e verifica se há itens proibidos na lista.
4.  **Veredito:** O sistema exibe instantaneamente se o recibo está **APROVADO** ou **REPROVADO** para reembolso.

---

## 🚀 Como Executar o Projeto

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/faelaphoenix/dio-ia-travel-auditor.git](https://github.com/faelaphoenix/dio-ia-travel-auditor.git)
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure suas chaves:**
    Crie um arquivo `.env` na raiz do projeto com suas credenciais da Azure (veja o modelo no repositório).

4.  **Rode a infraestrutura inicial:**
    ```bash
    python
