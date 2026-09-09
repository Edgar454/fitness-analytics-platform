terraform {

  required_version = ">= 1.11"

  backend "s3" {
    bucket       = "edgar-fitness-terraform-state"
    key          = "fitness-platform/terraform.tfstate"
    region       = "eu-west-1"
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}


provider "aws" {
  region = var.region
}