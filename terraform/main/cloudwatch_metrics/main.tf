resource "aws_cloudwatch_metric_alarm" "worker_queue_depth" {
  alarm_name          = "${var.project_name}-${var.queue_name}-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  statistic           = "Average"
  period              = 60

  threshold = var.queue_depth_threshold

  dimensions = {
    QueueName = var.queue_name
  }

  alarm_actions = [
    var.autoscaling_policy_arn
  ]
}