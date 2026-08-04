output "subnet_group_name" {
    value = aws_db_subnet_group.this.name
}

output "security_group_ids" {
    value = [aws_security_group.rds.id]
}