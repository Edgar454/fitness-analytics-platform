resource "aws_iam_role" "dispatcher" {
  name = "${var.project_name}-dispatcher"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [{
      Effect = "Allow"

      Principal = {
        Service = "lambda.amazonaws.com"
      }

      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "dispatcher" {
  name = "${var.project_name}-dispatcher"
  role = aws_iam_role.dispatcher.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "SendIngestionJobs"
        Effect = "Allow"

        Action = [
          "sqs:SendMessage"
        ]

        Resource = var.queue_arns
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "dispatcher_vpc" {
  role       = aws_iam_role.dispatcher.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# ECS execution role
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.project_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

#ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_policy" "worker_policies" {
  name = "${var.project_name}-worker-policies"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "SQSWorkerOperations"
        Effect = "Allow"

        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:ChangeMessageVisibility"
        ]

        Resource = [
          var.queue_arns
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_logs" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.worker_policies.arn
}