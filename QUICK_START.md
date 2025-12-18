# 🚀 Quick Start Guide

Guia rápido para começar a usar o sistema de detecção de fraudes.

## Pré-requisitos

- Java 17+
- Python 3.9+
- Docker e Docker Compose
- Maven 3.8+ (ou use o wrapper incluído)
- Azure CLI (para deploy na nuvem)

## Setup Local

### 1. Clone e Configure

```bash
git clone <seu-repositorio>
cd fraud-detection
```

### 2. Configure Variáveis de Ambiente

```bash
# Linux/Mac
cp .env.example .env

# Windows
copy .env.example .env
```

Edite o arquivo `.env` com suas configurações.

### 3. Inicie os Serviços

```bash
# Linux/Mac
./scripts/setup.sh

# Windows
.\scripts\setup.ps1
```

Ou manualmente:

```bash
docker-compose up -d
```

### 4. Configure Ambiente Python

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5. Inicie a API Java

```bash
cd api-java

# Linux/Mac
./mvnw spring-boot:run

# Windows
.\mvnw.cmd spring-boot:run
```

A API estará disponível em: http://localhost:8080

### 6. Acesse a Documentação

- Swagger UI: http://localhost:8080/swagger-ui.html
- API Docs: http://localhost:8080/v3/api-docs

## Testando o Sistema

### 1. Gerar Dados de Teste

```bash
python scripts/generate_data.py -n 100 -o data/transactions.json
```

### 2. Enviar Transação via API

```bash
curl -X POST http://localhost:8080/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "transactionId": "txn-123",
    "userId": "user-001",
    "amount": 1500.00,
    "currency": "BRL",
    "merchantId": "merchant-001",
    "merchantCategory": "Eletrônicos",
    "timestamp": "2024-01-15T10:30:00",
    "userCountry": "BR",
    "merchantCountry": "BR",
    "paymentMethod": "CREDIT_CARD"
  }'
```

### 3. Verificar Alertas

```bash
curl http://localhost:8080/api/v1/alerts
```

### 4. Verificar Métricas

```bash
curl http://localhost:8080/actuator/metrics
```

## Estrutura do Projeto

```
fraud-detection/
├── api-java/              # API Spring Boot
├── src/                   # Scripts Python
│   ├── data_ingestion/    # Ingestão de dados
│   ├── data_processing/   # Processamento
│   ├── data_storage/      # Armazenamento
│   ├── ml_models/         # Modelos ML
│   ├── monitoring/        # Monitoramento
│   └── utils/             # Utilitários
├── infrastructure/       # Terraform
├── notebooks/             # Jupyter notebooks
├── scripts/               # Scripts auxiliares
└── docs/                  # Documentação
```

## Próximos Passos

1. Leia o [README.md](README.md) completo
2. Consulte a [Documentação de Arquitetura](docs/ARCHITECTURE.md)
3. Veja o [Guia de Deployment](docs/DEPLOYMENT.md)
4. Prepare-se para a [Apresentação](docs/PRESENTATION.md)

## Troubleshooting

### API não inicia
- Verifique se a porta 8080 está livre
- Verifique as configurações do banco de dados no `.env`
- Veja os logs: `docker-compose logs api`

### Erros de conexão
- Verifique se todos os serviços estão rodando: `docker-compose ps`
- Verifique as variáveis de ambiente no `.env`
- Reinicie os serviços: `docker-compose restart`

### Problemas com Python
- Certifique-se de estar no ambiente virtual
- Reinstale as dependências: `pip install -r requirements.txt`

## Suporte

Para dúvidas ou problemas, consulte a documentação completa ou abra uma issue no repositório.

