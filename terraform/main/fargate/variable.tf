variable "project_name" {
  type = string
}

variable "worker_provider" {
  type = string
}

variable "ecr_image" {
  type = string
}

variable "queue_url" {
  type = string
}

variable "redis_url" {
  type = string
}

variable "region" {
  type = string
}

variable "database_host" {
  type = string
}

variable "database_password" {
  type      = string
  sensitive = true
}

variable "db_user" {
  type = string
}

variable "cert_path" {
  type = string
  default = "/app/ingestion/global-bundle.pem"
}

variable "log_group_name" {
  type = string
}

variable "cluster_id" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "ecs_execution_role_arn" {
  type = string
}

variable "ecs_task_role_arn" {
  type = string
}

variable "cpu" {
  type    = number
  default = 1024
}

variable "memory" {
  type    = number
  default = 2048
}

variable "min_capacity" {
  type    = number
  default = 0
}

variable "max_capacity" {
  type    = number
  default = 10
}

variable "scale_out_cooldown" {
  type    = number
  default = 60
}

variable "scale_out_step_1" {
  type    = number
  default = 1
}

variable "scale_out_step_2" {
  type    = number
  default = 2
}

variable "scale_out_step_3" {
  type    = number
  default = 3
}

variable "tags" {
  type = map(string)
}