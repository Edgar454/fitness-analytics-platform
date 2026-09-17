resource "aws_lambda_function" "dispatcher" {
  function_name = "${var.project_name}-dispatcher"

  role = var.dispatcher_role_arn
  tags = var.tags

  runtime = "python3.12"
  handler = "handler.lambda_handler"

  filename         = var.lambda_zip_path
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  timeout     = 60
  memory_size = 512

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [var.lambda_security_group_id]
  }

  environment {
    variables = {
      ACTIVE_USER_WINDOW_DAYS = tostring(var.active_user_window_days)

      GOOGLE_HEALTH_QUEUE_URL = var.google_health_queue_url
      FATSECRET_QUEUE_URL     = var.fatsecret_queue_url
      LYFTA_QUEUE_URL         = var.lyfta_queue_url

      DATABASE_HOST     = var.database_host
      DB_USER           = var.db_user
      DATABASE_PASSWORD = var.database_password

      CERT_PATH = var.cert_path
    }
  }
}