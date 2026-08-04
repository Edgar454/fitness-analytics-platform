variable "tags" {
    type = map(string)
}

variable "db_identifier" {
  type    = string
  default = "sportfolio-db"
}

variable "db_name" {
  type    = string
  default = "sportfolio"
}

variable "db_username" {
  type    = string
  default = "sportfolio_admin"
}

variable "db_password" {
  type    = string
  sensitive = true
}

variable "engine_version" {
  type    = string
  default = "18"
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "allocated_storage" {
  type    = number
  default = 20
}

variable "subnet_group_name" {
    type = string
}

variable "security_group_ids" {
    type = list(string)
}