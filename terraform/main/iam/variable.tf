variable "project_name" {
  type = string
}

variable "queue_arns" {
  type = list(string)
}

variable "kms_key_arn" {
  type = string
}

variable "tags" {
  type    = map(string)
  default = {}
}