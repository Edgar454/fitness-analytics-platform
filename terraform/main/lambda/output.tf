output "dispatcher_lambda_arn" {
  description = "ARN of the dispatcher Lambda"
  value       = aws_lambda_function.dispatcher.arn
}

output "dispatcher_lambda_name" {
  description = "Name of the dispatcher Lambda"
  value       = aws_lambda_function.dispatcher.function_name
}