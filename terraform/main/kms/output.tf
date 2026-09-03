output "key_id" {
  description = "ID of the KMS credentials key."
  value       = aws_kms_key.credentials.key_id
}

output "key_arn" {
  description = "ARN of the KMS credentials key."
  value       = aws_kms_key.credentials.arn
}

output "alias_arn" {
  description = "ARN of the KMS credentials key alias."
  value       = aws_kms_alias.credentials.arn
}