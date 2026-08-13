data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

module "progress_photo_s3" {
  source              = "./progress_photo_s3"
  tags                = local.common_tags
  progress_photo_bucket_name = var.progress_photo_bucket_name
}

module "sns" {
  source              = "./sns"
  tags                = local.common_tags
  project_name        = var.project_name
  alert_email         = var.alert_email
}


module "budgets" {
  source              = "./budgets"
  monthly_budget      = 10
  project_name        = var.project_name
  sns_topic_arn       = module.sns.topic_arn
}

module "secrets" {
  source              = "./secrets"
  tags                = local.common_tags
}

module "network" {
  source              = "./network"
  tags                = local.common_tags
  vpc_id              = data.aws_vpc.default.id
  subnet_ids          = data.aws_subnets.default.ids
  allowed_cidr_blocks = ["196.115.25.218/32"]
}

module "rds" {
  source              = "./rds"
  tags                = local.common_tags
  db_password         = module.secrets.db_password
  subnet_group_name   = module.network.subnet_group_name
  security_group_ids  = module.network.security_group_ids
}