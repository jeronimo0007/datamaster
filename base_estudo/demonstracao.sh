# Durante a apresentação, execute estes comandos:

# 1. Mostrar estrutura do projeto
tree -L 3 -I "__pycache__|*.pyc"

# 2. Deploy rápido com Terraform
cd infrastructure/terraform/environments/dev
terraform plan
terraform apply -auto-approve

# 3. Executar pipeline
python scripts/run_pipeline.py --env dev --demo

# 4. Abrir dashboard
streamlit run src/monitoring/dashboard.py

# 5. Testar API
curl -X POST http://localhost:8000/api/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{"transaction_id": "demo_001", "amount": 50000, "user_id": "test_user"}'

# 6. Mostrar Data Quality reports
open docs/dq_report.html

# 7. Mostrar métricas no Azure Monitor
az monitor metrics list --resource <resource-id> --metric "fraud_rate"