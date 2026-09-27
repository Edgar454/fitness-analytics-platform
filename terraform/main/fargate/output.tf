output "autoscaling_policy_arn" {
    value = aws_appautoscaling_policy.worker_scale_out.arn
}