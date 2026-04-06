variable "project" {
  description = "Project name prefix"
  type        = string
  default     = "documind"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus2"
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
  default     = "documind-prod-rg"
}

variable "node_count" {
  description = "Initial AKS node count"
  type        = number
  default     = 3
}

variable "node_vm_size" {
  description = "AKS node VM size"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "db_admin_user" {
  description = "PostgreSQL admin username"
  type        = string
  sensitive   = true
}

variable "db_admin_password" {
  description = "PostgreSQL admin password"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default = {
    project     = "documind"
    environment = "production"
    managed_by  = "terraform"
  }
}
