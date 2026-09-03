output "kms_key_id" {
  description = "ID of the KMS credentials key."
  value       = module.kms.key_id
}