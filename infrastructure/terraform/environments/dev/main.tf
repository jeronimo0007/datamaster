terraform {
  required_version = ">= 1.5"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
  
  backend "azurerm" {
    # Configurar backend do Azure Storage
    # resource_group_name  = "rg-terraform-state"
    # storage_account_name = "terraformstate"
    # container_name       = "tfstate"
    # key                  = "fraud-detection-dev.terraform.tfstate"
  }
}

provider "azurerm" {
  features {
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  
  tags = {
    Environment = "dev"
    Project     = "fraud-detection"
  }
}

# Storage Account (Data Lake Gen2)
resource "azurerm_storage_account" "datalake" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true  # Habilita Data Lake Gen2
  
  tags = azurerm_resource_group.main.tags
}

# Containers do Data Lake
resource "azurerm_storage_data_lake_gen2_filesystem" "raw" {
  name               = "raw"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "processed" {
  name               = "processed"
  storage_account_id = azurerm_storage_account.datalake.id
}

resource "azurerm_storage_data_lake_gen2_filesystem" "curated" {
  name               = "curated"
  storage_account_id = azurerm_storage_account.datalake.id
}

# Event Hubs Namespace
resource "azurerm_eventhub_namespace" "main" {
  name                = var.event_hub_namespace
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  capacity            = 1
  
  tags = azurerm_resource_group.main.tags
}

# Event Hub
resource "azurerm_eventhub" "transactions" {
  name                = "transactions"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 4
  message_retention   = 1
}

# Cosmos DB Account
resource "azurerm_cosmosdb_account" "main" {
  name                = "${var.project_name}-cosmos"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  
  consistency_policy {
    consistency_level = "Session"
  }
  
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
  
  tags = azurerm_resource_group.main.tags
}

# Cosmos DB Database
resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "fraud-detection"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

# Cosmos DB Container
resource "azurerm_cosmosdb_sql_container" "ml_models" {
  name                  = "ml-models"
  resource_group_name    = azurerm_resource_group.main.name
  account_name           = azurerm_cosmosdb_account.main.name
  database_name          = azurerm_cosmosdb_sql_database.main.name
  partition_key_path     = "/id"
  partition_key_version  = 1
  throughput             = 400
}

# Key Vault
resource "azurerm_key_vault" "main" {
  name                = "${var.project_name}-kv"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  
  tags = azurerm_resource_group.main.tags
}

data "azurerm_client_config" "current" {}

# PostgreSQL Server
resource "azurerm_postgresql_flexible_server" "main" {
  name                   = "${var.project_name}-postgres"
  resource_group_name    = azurerm_resource_group.main.name
  location               = azurerm_resource_group.main.location
  version                = "14"
  administrator_login    = var.db_admin_username
  administrator_password = var.db_admin_password
  sku_name               = "B_Standard_B1ms"
  
  tags = azurerm_resource_group.main.tags
}

# PostgreSQL Database
resource "azurerm_postgresql_flexible_server_database" "main" {
  name      = "fraud_detection"
  server_id = azurerm_postgresql_flexible_server.main.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

