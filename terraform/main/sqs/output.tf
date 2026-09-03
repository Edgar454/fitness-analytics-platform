output "google_health_queue_url" {
  description = "URL of the Google Health ingestion SQS queue."
  value       = aws_sqs_queue.google_health.url
}

output "fatsecret_queue_url" {
  description = "URL of the FatSecret ingestion SQS queue."
  value       = aws_sqs_queue.fatsecret.url
}

output "lyfta_queue_url" {
  description = "URL of the Lyfta ingestion SQS queue."
  value       = aws_sqs_queue.lyfta.url
}