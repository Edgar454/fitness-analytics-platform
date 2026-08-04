output "github_bootstrap_role_arn" {
  value = aws_iam_role.github_bootstrap_role
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}