variable "google_health_queue_name" {
  description = "Name of the Google Health ingestion SQS queue."
  type        = string
  default     = "health-platform-google-health"
}

variable "fatsecret_queue_name" {
  description = "Name of the FatSecret ingestion SQS queue."
  type        = string
  default     = "health-platform-fatsecret"
}

variable "lyfta_queue_name" {
  description = "Name of the Lyfta ingestion SQS queue."
  type        = string
  default     = "health-platform-lyfta"
}

variable "tags" {
  type        = map(string)
}