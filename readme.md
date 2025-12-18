# 🚀 Sistema de Detecção de Fraudes Bancárias - Azure Cloud Native

![Azure](https://img.shields.io/badge/Azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Spark](https://img.shields.io/badge/Apache_Spark-FFFFFF?style=for-the-badge&logo=apachespark&logoColor=#E35A16)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=for-the-badge&logo=mlflow&logoColor=white)

**Sistema de detecção de fraudes em tempo real para transações bancárias, implementado na Azure com arquitetura cloud-native, Data Quality automatizado e escalabilidade automática.**

## 📋 Sumário

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Quick Start](#-quick-start)
- [Componentes Azure](#-componentes-azure)
- [Comparativo Multi-Cloud](#-comparativo-multi-cloud)
- [Deployment](#-deployment)
- [Monitoramento](#-monitoramento)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🎯 Visão Geral

Solução completa de engenharia de dados para detecção de fraudes em transações bancárias, implementando todos os requisitos do case:

- ✅ **Extração de dados** de múltiplas fontes
- ✅ **Ingestão** batch e streaming
- ✅ **Armazenamento** multi-camada (Data Lake, Data Warehouse, NoSQL)
- ✅ **Observabilidade** completa do pipeline
- ✅ **Segurança e LGPD** com mascaramento de dados
- ✅ **Data Quality** automatizado
- ✅ **Machine Learning** em produção
- ✅ **Escalabilidade** automática

**Métricas de Performance:**
- ⏱️ **Latência:** < 2 segundos para detecção em tempo real
- 📊 **Precisão:** > 95% recall em fraudes
- 💰 **Custo:** ~R$ 3.000/mês para 10M transações/dia
- 🔝 **Disponibilidade:** 99.9% SLA

## 🏗️ Arquitetura

### Diagrama da Solução

```mermaid
graph TB
    A[Fontes de Dados] --> B[Azure Event Hubs]
    B --> C[Azure Databricks]
    C --> D[Azure Data Lake Gen2]
    C --> E[Azure Synapse Analytics]
    D --> F[Data Quality - Purview]
    E --> G[Power BI Dashboard]
    C --> H[Azure Machine Learning]
    H --> I[Modelos de Fraude]
    I --> J[API REST]
    J --> K[Sistemas de Alerta]
    
    L[Azure Monitor] -.->|Monitoramento| B
    L -.->|Monitoramento| C
    L -.->|Monitoramento| J
    
    M[Terraform] -->|IaC| N[Azure Resource Group]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style J fill:#ccf,stroke:#333,stroke-width:2px