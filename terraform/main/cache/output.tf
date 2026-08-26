output "primary_endpoint" {
  description = "Endpoint d'écriture (toujours valide, que ha_enabled soit true ou false)"
  value       = aws_elasticache_replication_group.this.primary_endpoint_address
}

output "reader_endpoint" {
  description = "Endpoint de lecture — pointe vers le replica si ha_enabled=true, sinon identique au primary"
  value       = aws_elasticache_replication_group.this.reader_endpoint_address
}

output "port" {
  value = aws_elasticache_replication_group.this.port
}

output "security_group_id" {
  value = aws_security_group.cache.id
}