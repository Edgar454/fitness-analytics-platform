variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "allowed_security_group_ids" {
  description = "Security groups autorisés à se connecter au cache (API+MCP, ingestion worker)"
  type        = list(string)
}

variable "node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "engine_version" {
  type    = string
  default = "7.1"
}

variable "ha_enabled" {
  description = "true pour la fenêtre de démo (primary + replica, failover auto) ; false le reste du temps (nœud unique)"
  type        = bool
  default     = false
}

variable "tags" {
  type    = map(string)
  default = {}
}