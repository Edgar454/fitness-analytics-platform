variable "project_name" {
  type = string
}

variable "tags" {
    type = map(string)
}

variable "dispatcher_role_arn" {
  type = string
}

variable "lambda_zip_path" {
  type = string
}

variable "active_user_window_days" {
  type    = number
  default = 30
}

variable "google_health_queue_url" {
  type = string
}

variable "fatsecret_queue_url" {
  type = string
}

variable "lyfta_queue_url" {
  type = string
}

variable "database_host" {
  type = string
}

variable "db_user" {
  type = string
}

variable "database_password" {
  type      = string
  sensitive = true
}

variable "cert_path" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "lambda_security_group_id" {
  type = string
}