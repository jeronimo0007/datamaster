# 1. Clone o repositório
git clone https://github.com/seu-usuario/fraud-detection-azure.git
cd fraud-detection-azure

# 2. Configure o ambiente
make setup

# 3. Deploy da infraestrutura (dev)
make deploy-dev

# 4. Execute o pipeline
make run-pipeline

# 5. Acesse o dashboard
make open-dashboard