resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

resource "aws_subnet" "public-a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[0]
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-public-subnet"
    }
  )
}

resource "aws_subnet" "private-a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[0]
  availability_zone = var.availability_zone[0]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-private-subnet"
    }
  )
}

resource "aws_subnet" "private-b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[1]
  availability_zone = var.availability_zone[1]

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-private-subnet"
    }
  )
}

resource "aws_db_subnet_group" "this" {
  name       = "sportfolio-db-subnet-group"
  subnet_ids = [aws_subnet.private-a.id , aws_subnet.private-b.id ]

  tags = var.tags
}