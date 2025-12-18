#!/bin/bash

# Script de setup do ambiente de desenvolvimento

set -e

echo "🚀 Configurando ambiente de desenvolvimento..."

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.9+"
    exit 1
fi

# Verifica Java
if ! command -v java &> /dev/null; then
    echo "❌ Java não encontrado. Por favor, instale Java 17+"
    exit 1
fi

# Verifica Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale Docker"
    exit 1
fi

# Cria ambiente virtual Python
echo "📦 Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instala dependências Python
echo "📦 Instalando dependências Python..."
pip install --upgrade pip
pip install -r requirements.txt

# Configura variáveis de ambiente
echo "⚙️  Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado. Por favor, configure as variáveis."
fi

# Inicia serviços com Docker Compose
echo "🐳 Iniciando serviços com Docker Compose..."
docker-compose up -d

# Aguarda serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Executa migrações (se houver)
echo "🗄️  Executando migrações..."
# Adicione comandos de migração aqui se necessário

echo "✅ Ambiente configurado com sucesso!"
echo ""
echo "Próximos passos:"
echo "1. Configure o arquivo .env com suas credenciais"
echo "2. Execute: source venv/bin/activate"
echo "3. Execute: cd api-java && ./mvnw spring-boot:run"
echo "4. Acesse: http://localhost:8080/swagger-ui.html"

