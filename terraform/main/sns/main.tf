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