variable "bucket_name" {
    type = string
}

variable "progress_photo_bucket_name" {
    type = string
}

variable "region" {
    type = string
}

variable "project_name" {
    type = string
}

variable "alert_email" {
    type = string
}


variable "lambda_zip_path" {
  type = string
}


variable "active_user_window_days" {
  type    = number
  default = 30
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