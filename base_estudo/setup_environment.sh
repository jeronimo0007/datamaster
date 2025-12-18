#!/bin/bash

# Script de setup do ambiente
# Configura tudo necessário para executar o projeto

set -e

echo "🚀 Configurando ambiente de desenvolvimento"
echo "=========================================="

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Funções
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Verificar se está no diretório correto
if [ ! -f "README.md" ]; then
    print_error "Execute este script do diretório raiz do projeto"
    exit 1
fi

# 1. Verificar Python
print_info "1. Verificando Python..."
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 não encontrado. Instale Python 3.9 ou superior"
    exit 1
fi

# 2. Verificar pip
print_info "2. Verificando pip..."
if command -v pip3 &>/dev/null; then
    print_success "pip encontrado"
else
    print_error "pip não encontrado"
    exit 1
fi

# 3. Criar ambiente virtual
print_info "3. Criando ambiente virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_success "Ambiente virtual criado"
else
    print_success "Ambiente virtual já existe"
fi

# 4. Ativar ambiente virtual
print_info "4. Ativando ambiente virtual..."
source .venv/bin/activate

# 5. Atualizar pip
print_info "5. Atualizando pip..."
pip install --upgrade pip

# 6. Instalar dependências
print_info "6. Instalando dependências..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 7. Instalar pre-commit hooks
print_info "7. Configurando pre-commit..."
pre-commit install

# 8. Criar diretórios necessários
print_info "8. Criando estrutura de diretórios..."
mkdir -p data/{raw,processed,curated}
mkdir -p logs/{api,dashboard,pipeline}
mkdir -p models
mkdir -p config

# 9. Copiar arquivos de configuração
print_info "9. Configurando arquivos de ambiente..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Arquivo .env criado. Edite com suas configurações"
else
    print_success "Arquivo .env já existe"
fi

if [ ! -f "config/dev.yaml" ]; then
    cp config/dev.yaml.example config/dev.yaml
    print_success "Configuração dev criada"
fi

# 10. Configurar Git hooks
print_info "10. Configurando Git hooks..."
if [ -d ".git" ]; then
    git config core.hooksPath .githooks
    chmod +x .githooks/*
    print_success "Git hooks configurados"
else
    print_info "Diretório .git não encontrado, pulando Git hooks"
fi

# 11. Verificar Docker
print_info "11. Verificando Docker..."
if command -v docker &>/dev/null; then
    print_success "Docker encontrado"
    
    if command -v docker-compose &>/dev/null; then
        print_success "Docker Compose encontrado"
    else
        print_error "Docker Compose não encontrado"
    fi
else
    print_info "Docker não encontrado. Algumas funcionalidades não estarão disponíveis"
fi

# 12. Verificar Terraform
print_info "12. Verificando Terraform..."
if command -v terraform &>/dev/null; then
    TERRAFORM_VERSION=$(terraform --version | head -n1 | cut -d' ' -f2)
    print_success "Terraform $TERRAFORM_VERSION encontrado"
else
    print_info "Terraform não encontrado. Necessário para deploy na cloud"
fi

# 13. Verificar Azure CLI
print_info "13. Verificando Azure CLI..."
if command -v az &>/dev/null; then
    AZ_VERSION=$(az --version | grep "azure-cli" | head -n1 | cut -d' ' -f2)
    print_success "Azure CLI $AZ_VERSION encontrado"
else
    print_info "Azure CLI não encontrado. Necessário para deploy no Azure"
fi

echo ""
echo "=========================================="
print_success "✅ Setup concluído com sucesso!"
echo ""

print_info "Próximos passos:"
echo "1. Edite o arquivo .env com suas configurações"
echo "2. Execute 'make test' para verificar a instalação"
echo "3. Execute 'docker-compose up -d' para subir serviços locais"
echo "4. Execute 'make run-pipeline' para testar o pipeline"
echo ""
print_info "Comandos úteis:"
echo "  make help          - Mostra todos os comandos disponíveis"
echo "  make test          - Executa testes"
echo "  make deploy-dev    - Deploy no ambiente dev"
echo "  make monitor       - Inicia dashboard de monitoramento"
echo ""
print_success "🎉 Ambiente configurado e pronto para uso!"