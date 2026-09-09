resource "aws_iam_role" "github_bootstrap_role" {
  name               = "github-bootstrap-role"
  assume_role_policy = var.github_oidc_assume_json 
}

resource "aws_iam_policy" "terraform_bootstrap" {
  name = "github-terraform-bootstrap"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Sid    = "RDSInstanceLifecycle"
        Effect = "Allow"
        Action = [
          "rds:CreateDBInstance",
          "rds:DeleteDBInstance",
          "rds:ModifyDBInstance",
          "rds:DescribeDBInstances",
          "rds:StopDBInstance",
          "rds:StartDBInstance",
          "rds:AddTagsToResource",
          "rds:RemoveTagsFromResource",
          "rds:ListTagsForResource"
        ]
        Resource = "*"
      },
      {
        Sid    = "RDSSubnetAndParamGroups"
        Effect = "Allow"
        Action = [
          "rds:CreateDBSubnetGroup",
          "rds:DeleteDBSubnetGroup",
          "rds:ModifyDBSubnetGroup",
          "rds:DescribeDBSubnetGroups",
          "rds:CreateDBParameterGroup",
          "rds:DeleteDBParameterGroup",
          "rds:ModifyDBParameterGroup",
          "rds:DescribeDBParameterGroups",
          "rds:DescribeDBParameters"
        ]
        Resource = "*"
      },
      {
        Sid    = "TerraformStateBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = "arn:aws:s3:::edgar-fitness-terraform-state"
      },
      {
        Sid    = "TerraformStateObject"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]
        Resource = "arn:aws:s3:::edgar-fitness-terraform-state/fitness-platform/terraform.tfstate"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bootstrap" {
  role       = aws_iam_role.github_bootstrap_role.name
  policy_arn = aws_iam_policy.terraform_bootstrap.arn
}