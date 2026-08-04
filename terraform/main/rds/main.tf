# --- RDS instance ---

resource "aws_db_instance" "this" {
  identifier     = var.db_identifier
  engine         = "postgres"
  engine_version = var.engine_version

  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = var.subnet_group_name 
  vpc_security_group_ids = var.security_group_ids 
  publicly_accessible    = true

  backup_retention_period = 1
  skip_final_snapshot     = true
  deletion_protection     = false

  tags = var.tags
}