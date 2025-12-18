# Deploy completo
cd infrastructure/terraform/environments/dev
terraform init
terraform plan
terraform apply -auto-approve

# Outputs
terraform output databricks_workspace_url
terraform output synapse_server_name
terraform output api_endpoint