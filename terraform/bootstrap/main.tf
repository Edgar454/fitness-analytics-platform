module "s3" {
  source = "./s3"
  bucket_name = var.bucket_name
}

module "iam" {
    source = "./iam"
    github_oidc_assume_json = data.aws_iam_policy_document.github_oidc_assume.json
}