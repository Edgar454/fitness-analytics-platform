resource "aws_iam_role" "github_bootstrap_role" {
  name               = "github-bootstrap-role"
  assume_role_policy = var.github_oidc_assume_json
}

resource "aws_iam_policy" "terraform_bootstrap" {
  name = "github-terraform-bootstrap"

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [

      # ============================================================
      # RDS
      # ============================================================

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

      # ============================================================
      # EC2 / VPC
      # ============================================================

      
      {
        Sid    = "EC2NetworkingRead"
        Effect = "Allow"
        Action = [
          "ec2:DescribeVpcs",
          "ec2:DescribeVpcAttribute",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeRouteTables",
          "ec2:DescribeAvailabilityZones"
        ]
        Resource = "*"
      },

      # ============================================================
      # S3 - Terraform state
      # ============================================================

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
        Resource = [
          "arn:aws:s3:::edgar-fitness-terraform-state/fitness-platform/terraform.tfstate",
          "arn:aws:s3:::edgar-fitness-terraform-state/fitness-platform/terraform.tfstate.tflock"
        ]
      },
      {
        Sid    = "ProgressPhotoBucketRead"
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:GetBucketPublicAccessBlock",
          "s3:GetBucketTagging",
          "s3:GetBucketAcl",
          "s3:GetBucketCORS",
          "s3:GetBucketWebsite"
        ]
        Resource = "arn:aws:s3:::edgar-fitness-progess-photos"
      },

      # ============================================================
      # S3 - Application buckets
      # ============================================================

      {
        Sid    = "S3BucketLifecycle"
        Effect = "Allow"
        Action = [
          "s3:CreateBucket",
          "s3:DeleteBucket",
          "s3:GetBucketLocation",
          "s3:GetBucketVersioning",
          "s3:PutBucketVersioning",
          "s3:GetPublicAccessBlock",
          "s3:PutPublicAccessBlock",
          "s3:DeletePublicAccessBlock",
          "s3:GetBucketPolicy",
          "s3:PutBucketPolicy",
          "s3:DeleteBucketPolicy",
          "s3:GetBucketTagging",
          "s3:PutBucketTagging",
          "s3:GetBucketPublicAccessBlock",
          "s3:PutBucketPublicAccessBlock",
        ]
        Resource = "*"
      },

      # ============================================================
      # KMS
      # ============================================================

      {
        Sid    = "KMSKeyLifecycle"
        Effect = "Allow"
        Action = [
          "kms:CreateKey",
          "kms:DescribeKey",
          "kms:GetKeyRotationStatus",
          "kms:EnableKey",
          "kms:DisableKey",
          "kms:ScheduleKeyDeletion",
          "kms:CancelKeyDeletion",
          "kms:EnableKeyRotation",
          "kms:DisableKeyRotation",
          "kms:PutKeyPolicy",
          "kms:GetKeyPolicy",
          "kms:ListKeyPolicies",
          "kms:TagResource",
          "kms:UntagResource",
          "kms:ListResourceTags",
        ]
        Resource = "*"
      },

      {
        Sid    = "KMSAliasLifecycle"
        Effect = "Allow"
        Action = [
          "kms:CreateAlias",
          "kms:UpdateAlias",
          "kms:DeleteAlias",
          "kms:ListAliases"
        ]
        Resource = "*"
      },

      # ============================================================
      # Secrets Manager
      # ============================================================

      {
        Sid    = "SecretsManagerLifecycle"
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:RestoreSecret",
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:PutSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:UpdateSecretVersionStage",
          "secretsmanager:TagResource",
          "secretsmanager:UntagResource",
          "secretsmanager:GetResourcePolicy",
        ]
        Resource = "*"
      },

      # ============================================================
      # SNS
      # ============================================================

      {
        Sid    = "SNSLifecycle"
        Effect = "Allow"
        Action = [
          "sns:CreateTopic",
          "sns:DeleteTopic",
          "sns:GetTopicAttributes",
          "sns:SetTopicAttributes",
          "sns:TagResource",
          "sns:UntagResource",
          "sns:ListTags",
          "sns:ListTagsForResource",
          "sns:GetSubscriptionAttributes",

          "sns:CreateSubscription",
          "sns:DeleteSubscription",
          "sns:GetSubscriptionAttributes",
          "sns:SetSubscriptionAttributes",
          "sns:Subscribe"
        ]
        Resource = "*"
      },

      # ============================================================
      # SQS
      # ============================================================

      {
        Sid    = "SQSLifecycle"
        Effect = "Allow"
        Action = [
          "sqs:CreateQueue",
          "sqs:DeleteQueue",
          "sqs:GetQueueAttributes",
          "sqs:SetQueueAttributes",
          "sqs:GetQueueUrl",
          "sqs:TagQueue",
          "sqs:UntagQueue",
          "sqs:ListQueueTags",
        ]
        Resource = "*"
      },

      # ============================================================
      # ElastiCache
      # ============================================================

      {
        Sid    = "ElastiCacheLifecycle"
        Effect = "Allow"
        Action = [
          "elasticache:CreateCacheCluster",
          "elasticache:DeleteCacheCluster",
          "elasticache:ModifyCacheCluster",
          "elasticache:DescribeCacheClusters",
          "elasticache:CreateReplicationGroup",
          "elasticache:DeleteReplicationGroup",
          "elasticache:ModifyReplicationGroup",
          "elasticache:DescribeReplicationGroups",
          "elasticache:CreateCacheSubnetGroup",
          "elasticache:DeleteCacheSubnetGroup",
          "elasticache:ModifyCacheSubnetGroup",
          "elasticache:DescribeCacheSubnetGroups",
          "elasticache:AddTagsToResource",
          "elasticache:RemoveTagsFromResource",
          "elasticache:ListTagsForResource"
        ]
        Resource = "*"
      },

      # ============================================================
      # Lambda
      # ============================================================

      {
        Sid    = "LambdaLifecycle"
        Effect = "Allow"
        Action = [
          "lambda:CreateFunction",
          "lambda:DeleteFunction",
          "lambda:UpdateFunctionCode",
          "lambda:UpdateFunctionConfiguration",
          "lambda:GetFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:PublishVersion",
          "lambda:DeleteFunctionUrlConfig",
          "lambda:CreateFunctionUrlConfig",
          "lambda:UpdateFunctionUrlConfig",
          "lambda:AddPermission",
          "lambda:RemovePermission",
          "lambda:TagResource",
          "lambda:UntagResource",
          "lambda:ListTags",
          "lambda:ListVersionsByFunction"
        ]
        Resource = "*"
      },

      # ============================================================
      # AWS Budgets
      # ============================================================

      {
        Sid    = "BudgetsLifecycle"
        Effect = "Allow"
        Action = [
          "budgets:ViewBudget",
          "budgets:CreateBudget",
          "budgets:ModifyBudget",
          "budgets:DeleteBudget",
          "budgets:DescribeBudget",
          "budgets:ListTagsForResource",
        ]
        Resource = "*"
      },

      # ============================================================
      # IAM - Lambda execution roles
      # ============================================================

      {
        Sid    = "LambdaExecutionRoleLifecycle"
        Effect = "Allow"
        Action = [
          "iam:CreateRole",
          "iam:DeleteRole",
          "iam:GetRole",
          "iam:UpdateRole",
          "iam:PutRolePolicy",
          "iam:DeleteRolePolicy",
          "iam:AttachRolePolicy",
          "iam:DetachRolePolicy",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "iam:TagRole",
          "iam:UntagRole"
        ]
        Resource = "*"
      },

      {
        Sid    = "LambdaPassRole"
        Effect = "Allow"
        Action = [
          "iam:PassRole"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bootstrap" {
  role       = aws_iam_role.github_bootstrap_role.name
  policy_arn = aws_iam_policy.terraform_bootstrap.arn
}