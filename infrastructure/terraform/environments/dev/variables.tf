variable "resource_group_name" {
  description = "Nome do Resource Group"
  type        = string
  default     = "rg-fraud-detection-dev"
}

variable "location" {
  description = "Região do Azure"
  type        = string
  default     = "brazilsouth"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "fraud-detection"
}

variable "storage_account_name" {
  description = "Nome da Storage Account (deve ser único globalmente)"
  type        = string
  default     = "fraudstoragedev"
}

variable "event_hub_namespace" {
  description = "Namespace do Event Hub"
  type        = string
  default     = "fraud-events-dev"
}

variable "db_admin_username" {
  description = "Usuário administrador do banco de dados"
  type        = string
  default     = "fraudadmin"
  sensitive   = true
}

variable "db_admin_password" {
  description = "Senha do administrador do banco de dados"
  type        = string
  sensitive   = true
}

