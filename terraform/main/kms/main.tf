resource "aws_kms_key" "credentials" {
  description         = "KMS key used to encrypt user provider credentials."
  enable_key_rotation = true

  tags = var.tags
}

resource "aws_kms_alias" "credentials" {
  name          = "alias/${var.key_alias}"
  target_key_id = aws_kms_key.credentials.key_id
}