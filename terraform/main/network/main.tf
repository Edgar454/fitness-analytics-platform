# --- Security group ---

resource "aws_security_group" "rds" {
  name        = "sportfolio-rds-sg"
  description = "Allow Postgres access from allowed IPs"
  vpc_id      = var.vpc_id
  tags = var.tags

  ingress {
    description = "Postgres from allowed IPs"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Subnet group ---

resource "aws_db_subnet_group" "this" {
  name       = "sportfolio-db-subnet-group"
  subnet_ids = var.subnet_ids
  tags = var.tags
}
