# Deploy com scripts
./scripts/deploy_azure.sh --env dev --region brazilsouth

# Ou passo a passo
az group create --name rg-fraud-detection --location brazilsouth
az deployment group create --resource-group rg-fraud-detection --template-file infrastructure/arm_templates/main.json