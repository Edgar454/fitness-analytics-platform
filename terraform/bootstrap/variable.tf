variable "bucket_name" {
    type = string
}

variable "region" {
    type = string
}

variable "github_repository_subject" {
  description = "GitHub Actions OIDC subject prefix."
  type        = string

  default = "Edgar454@125728220/fitness-analytics-platform@1307995812"
}