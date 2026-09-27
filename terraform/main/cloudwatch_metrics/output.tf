output "queue_depth_metric_name" {
    value =  aws_cloudwatch_metric_alarm.worker_queue_depth.name
}

output "queue_depth_metric_arn" {
    value =  aws_cloudwatch_metric_alarm.worker_queue_depth.arn
}