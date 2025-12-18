# Azure Purview - Data Quality
from azure.purview.scanning import PurviewScanningClient
from azure.purview.catalog import PurviewCatalogClient

# Configurar scanner
client = PurviewScanningClient(
    endpoint="https://{account}.purview.azure.com",
    credential=DefaultAzureCredential()
)

# Criar regras DQ
dq_rules = {
    "rules": [
        {
            "name": "amount_not_null",
            "ruleType": "NotNull",
            "columnName": "amount"
        },
        {
            "name": "amount_range",
            "ruleType": "Range",
            "columnName": "amount",
            "minValue": 0,
            "maxValue": 1000000
        }
    ]
}