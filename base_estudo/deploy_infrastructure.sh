#!/bin/bash

# Script de deploy da infraestrutura no Azure

set -e

echo "🚀 Deploy da infraestrutura no Azure"
echo "====================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Parâmetros
ENVIRONMENT=${1:-dev}
LOCATION=${2:-brazilsouth}
RESOURCE_GROUP="rg-fraud-detection-$ENVIRONMENT"

# Funções
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar Azure CLI
print_info "1. Verificando Azure CLI..."
if ! command -v az &>/dev/null; then
    print_error "Azure CLI não encontrado. Instale: https://docs.microsoft.com/cli/azure/install-azure-cli"
fi

# Login no Azure
print_info "2. Fazendo login no Azure..."
az login --use-device-code

# Definir subscription
print_info "3. Configurando subscription..."
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
if [ -z "$SUBSCRIPTION_ID" ]; then
    print_error "Não foi possível obter subscription ID"
fi

az account set --subscription $SUBSCRIPTION_ID

# Criar Resource Group
print_info "4. Criando Resource Group..."
if az group show --name $RESOURCE_GROUP &>/dev/null; then
    print_success "Resource Group já existe"
else
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --tags Environment=$ENVIRONMENT Application="FraudDetection"
    print_success "Resource Group criado: $RESOURCE_GROUP"
fi

# Deploy Terraform
print_info "5. Deploy com Terraform..."
cd infrastructure/terraform/environments/$ENVIRONMENT

if [ ! -f "terraform.tfvars" ]; then
    print_info "Criando terraform.tfvars..."
    cat > terraform.tfvars << EOF
environment = "$ENVIRONMENT"
location = "$LOCATION"
subscription_id = "$SUBSCRIPTION_ID"
resource_group_name = "$RESOURCE_GROUP"

# Tags
tags = {
  Environment = "$ENVIRONMENT"
  Application = "FraudDetection"
  ManagedBy = "Terraform"
}
EOF
fi

# Inicializar Terraform
terraform init -upgrade

# Validar configuração
terraform validate

# Plan
print_info "6. Planejando deploy..."
terraform plan -out=tfplan

# Aplicar
print_info "7. Aplicando configuração..."
terraform apply tfplan

# Obter outputs
print_info "8. Coletando outputs..."
DATABRICKS_URL=$(terraform output -raw databricks_workspace_url)
SYNAPSE_SERVER=$(terraform output -raw synapse_server_name)
DATA_LAKE_NAME=$(terraform output -raw data_lake_name)
API_ENDPOINT=$(terraform output -raw api_endpoint 2>/dev/null || echo "Não configurado")

print_success "✅ Deploy da infraestrutura concluído!"
echo ""
print_info "📊 Recursos criados:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Data Lake: $DATA_LAKE_NAME"
echo "  Databricks: $DATABRICKS_URL"
echo "  Synapse: $SYNAPSE_SERVER"
echo "  API: $API_ENDPOINT"
echo ""
print_info "🔧 Próximos passos:"
echo "1. Configurar secrets no Key Vault:"
echo "   az keyvault secret set --vault-name kv-fraud-$ENVIRONMENT --name databricks-token --value <token>"
echo ""
echo "2. Configurar pipelines no Data Factory:"
echo "   az datafactory pipeline create-run --factory-name adf-fraud-$ENVIRONMENT --name pl-fraud-detection"
echo ""
echo "3. Upload de notebooks para Databricks:"
echo "   python scripts/upload_databricks_notebooks.py"
echo ""
print_success "🎉 Infraestrutura pronta para uso!"