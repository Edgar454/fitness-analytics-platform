resource "aws_s3_bucket" "progress_photos" {
  bucket = var.progress_photo_bucket_name
  tags   = var.tags
}

resource "aws_s3_bucket_versioning" "progress_photos" {
  bucket = aws_s3_bucket.progress_photos.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "progress_photos" {
  bucket = aws_s3_bucket.progress_photos.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

