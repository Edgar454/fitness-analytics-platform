# --- Security groups ---

resource "aws_security_group" "rds" {
  name        = "sportfolio-rds-sg"
  description = "Allow Postgres access from allowed IPs and ECS/Lambda"
  vpc_id      = aws_vpc.main.id

  lifecycle {
    create_before_destroy = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_security_group" "lambda" {
  name        = "sportfolio-lambda-sg"
  description = "Security group for dispatcher Lambda"
  vpc_id      = aws_vpc.main.id

  lifecycle {
    create_before_destroy = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_security_group" "ecs" {
  name        = "sportfolio-ecs-sg"
  description = "Security group for ECS ingestion workers"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

resource "aws_security_group" "vpc_endpoint" {
  name        = "sportfolio-vpc-endpoint-sg"
  description = "Security group for VPC interface endpoints"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}


# --- VPC endpoint ---

resource "aws_vpc_endpoint" "sqs" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.sqs"
  vpc_endpoint_type = "Interface"

  subnet_ids = [
    aws_subnet.private-a.id
  ]

  security_group_ids = [
    aws_security_group.vpc_endpoint.id
  ]

  private_dns_enabled = true

  tags = var.tags
}


# --- RDS security group rules ---

resource "aws_security_group_rule" "rds_from_allowed_ips" {
  type              = "ingress"
  security_group_id = aws_security_group.rds.id

  description = "Postgres from allowed IPs"

  from_port   = 5432
  to_port     = 5432
  protocol    = "tcp"
  cidr_blocks = var.allowed_cidr_blocks
}

resource "aws_security_group_rule" "rds_from_lambda" {
  type                     = "ingress"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.lambda.id

  description = "Postgres from dispatcher Lambda"

  from_port = 5432
  to_port   = 5432
  protocol  = "tcp"
}

resource "aws_security_group_rule" "rds_from_ecs" {
  type                     = "ingress"
  security_group_id        = aws_security_group.rds.id
  source_security_group_id = aws_security_group.ecs.id

  description = "Postgres from ECS ingestion workers"

  from_port = 5432
  to_port   = 5432
  protocol  = "tcp"
}


# --- VPC endpoint security group rules ---

resource "aws_security_group_rule" "vpc_endpoint_from_lambda" {
  type                     = "ingress"
  security_group_id        = aws_security_group.vpc_endpoint.id
  source_security_group_id = aws_security_group.lambda.id

  description = "HTTPS from dispatcher Lambda"

  from_port = 443
  to_port   = 443
  protocol  = "tcp"
}

resource "aws_security_group_rule" "vpc_endpoint_from_ecs" {
  type                     = "ingress"
  security_group_id        = aws_security_group.vpc_endpoint.id
  source_security_group_id = aws_security_group.ecs.id

  description = "HTTPS from ECS ingestion workers"

  from_port = 443
  to_port   = 443
  protocol  = "tcp"
}