variable "key_alias" {
  description = "Alias of the KMS key."
  type        = string
  default     = "health-platform-credentials"
}

variable "tags" {
  description = "Mandatory tags applied to the KMS key."
  type        = map(string)
}