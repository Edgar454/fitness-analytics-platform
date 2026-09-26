resource "aws_ecr_repository" "health_worker" {

  name = "${var.project_name}-worker"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
  
  force_delete = true
  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "health_worker" {

  repository = aws_ecr_repository.health_worker.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 images"

        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 20
        }

        action = {
          type = "expire"
        }
      }
    ]
  })
}