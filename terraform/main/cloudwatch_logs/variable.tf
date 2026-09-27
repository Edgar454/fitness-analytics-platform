variable "project_name" {
  type = string
}

variable "tags" {
  type = map(string)
}

variable "queue_name" {
  type = string
}

variable "retention_in_days" {
  type= number
  default = 30
}
