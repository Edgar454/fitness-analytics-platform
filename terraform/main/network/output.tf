output "private_subnet_ids" {
    value = [aws_subnet.private.id]
}

output "subnet_group_name" {
    value = aws_db_subnet_group.this.name
}

output "security_group_ids" {
    value = [aws_security_group.rds.id]
}

output "lambda_security_group_id" {
    value = aws_security_group.lambda.id
}

output "ecs_security_group_id" {
    value = aws_security_group.ecs.id
}

