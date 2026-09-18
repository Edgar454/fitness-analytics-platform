# --- Security group ---

resource "aws_security_group" "rds" {
  name        = "sportfolio-rds-sg"
  description = "Allow Postgres access from allowed IPs"
  vpc_id      = var.vpc_id
  tags = var.tags

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "lambda" {
  name        = "sportfolio-lambda-sg"
  description = "Security group for dispatcher Lambda"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol     = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# --- Subnet group ---

resource "aws_db_subnet_group" "this" {
  name       = "sportfolio-db-subnet-group"
  subnet_ids = var.subnet_ids
  tags = var.tags
}

# ---  security group rules ---

# Allow inbound traffic from allowed ips
resource "aws_security_group_rule" "rds_from_allowed_ips" {
  type              = "ingress"
  security_group_id = aws_security_group.rds.id

  description = "Postgres from allowed IPs"

  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = var.allowed_cidr_blocks
}

# Allow inbound traffic from lambda
resource "aws_security_group_rule" "rds_from_lambda" {
  type                     = "ingress"

  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.lambda.id

  from_port = 5432
  to_port   = 5432
  protocol  = "tcp"
}