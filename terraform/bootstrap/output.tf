output "github_bootstrap_role_arn" {
  value = module.iam.github_bootstrap_role_arn
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}