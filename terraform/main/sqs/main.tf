resource "aws_sqs_queue" "google_health" {
  name = var.google_health_queue_name

  tags = var.tags
}

resource "aws_sqs_queue" "fatsecret" {
  name = var.fatsecret_queue_name

  tags = var.tags
}

resource "aws_sqs_queue" "lyfta" {
  name = var.lyfta_queue_name

  tags = var.tags
}