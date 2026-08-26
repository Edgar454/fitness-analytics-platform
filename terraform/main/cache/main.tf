# --- Subnet group : où ElastiCache peut placer ses nœuds ---

resource "aws_elasticache_subnet_group" "this" {
  name       = "sportfolio-cache-subnet-group"
  subnet_ids = var.subnet_ids
}

# --- Security group : accès uniquement depuis l'API+MCP et les workers d'ingestion ---

resource "aws_security_group" "cache" {
  name        = "sportfolio-cache-sg"
  description = "Allow Redis access from API and ingestion workers only"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Redis from allowed security groups"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = var.allowed_security_group_ids
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# --- Groupe de réplication : nœud unique par défaut, bascule HA via var.ha_enabled ---
#
# Un seul groupe de réplication couvre les deux modes :
#   - ha_enabled = false -> num_cache_clusters = 1 (pas de failover, pas de replica)
#   - ha_enabled = true  -> num_cache_clusters = 2 (primary + replica, failover automatique)
# Permet de basculer d'un mode à l'autre avec un seul `terraform apply`,
# sans recréer la ressource ni changer l'endpoint applicatif.

resource "aws_elasticache_replication_group" "this" {
  replication_group_id = "sportfolio-cache"
  description           = "Redis cache for API reads and distributed rate limiting"

  engine         = "redis"
  engine_version = var.engine_version
  node_type      = var.node_type

  num_cache_clusters          = var.ha_enabled ? 2 : 1
  automatic_failover_enabled  = var.ha_enabled
  multi_az_enabled            = var.ha_enabled

  subnet_group_name  = aws_elasticache_subnet_group.this.name
  security_group_ids = [aws_security_group.cache.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = var.tags
}