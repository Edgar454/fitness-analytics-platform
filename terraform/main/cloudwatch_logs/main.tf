resource "aws_cloudwatch_log_group" "worker" {
  name              = "/ecs/${var.project_name}/${var.queue_name}-worker-logs"
  retention_in_days = var.retention_in_days

  tags = var.tags
}
