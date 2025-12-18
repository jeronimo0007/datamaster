output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "storage_account_name" {
  value = azurerm_storage_account.datalake.name
}

output "event_hub_namespace" {
  value = azurerm_eventhub_namespace.main.name
}

output "event_hub_name" {
  value = azurerm_eventhub.transactions.name
}

output "cosmos_db_endpoint" {
  value = azurerm_cosmosdb_account.main.endpoint
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "postgresql_server_name" {
  value = azurerm_postgresql_flexible_server.main.name
}

