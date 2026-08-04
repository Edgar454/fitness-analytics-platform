resource "aws_budgets_budget" "project_budget" {

  name         = "${var.project_name}-monthly-budget"
  budget_type  = "COST"
  limit_amount = var.monthly_budget
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  cost_filter {
    name = "TagKeyValue"
    values = [
      format("Project$%s", var.project_name)
    ]
  }

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 50
    threshold_type      = "PERCENTAGE"

    notification_type = "ACTUAL"

    subscriber_sns_topic_arns = [
      var.sns_topic_arn
    ]
  }

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 100
    threshold_type      = "PERCENTAGE"

    notification_type = "ACTUAL"

    subscriber_sns_topic_arns = [
      var.sns_topic_arn
    ]
  }

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 150
    threshold_type      = "PERCENTAGE"

    notification_type = "ACTUAL"

    subscriber_sns_topic_arns = [
      var.sns_topic_arn
    ]
  }
}