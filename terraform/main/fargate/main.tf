resource "aws_ecs_task_definition" "worker" {
  family                   = "${var.project_name}-${var.worker_provider}"

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  cpu    = var.cpu
  memory = var.memory

  execution_role_arn = var.ecs_execution_role_arn
  task_role_arn      = var.ecs_task_role_arn

  container_definitions = jsonencode([
    {
      name      = "worker"
      image     = var.ecr_image
      essential = true

      environment = [
        {
          name  = "WORKER_PROVIDER"
          value = var.worker_provider
        },
        {
          name  = "QUEUE_URL"
          value = var.queue_url
        },
        {
          name  = "REDIS_URL"
          value = var.redis_url
        },
        {
          name  = "AWS_REGION"
          value = var.region
        },
        {
          name  = "DATABASE_HOST"
          value = var.database_host
        },
        {
          name  = "DATABASE_PASSWORD"
          value = var.database_password
        },
        {
          name  = "DB_USER"
          value = var.db_user
        },
        {
          name  = "CERT_PATH"
          value = var.cert_path
        },
        {
          name  = "LOAD_TEST"
          value = var.load_test_enabled
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"

        options = {
          awslogs-group         = var.log_group_name
          awslogs-region        = var.region
          awslogs-stream-prefix = "worker"
        }
      }
    }
  ])

  tags = var.tags
}


resource "aws_ecs_service" "worker" {
  name            = "${var.project_name}-${var.worker_provider}-worker"
  cluster         = var.cluster_id
  task_definition = aws_ecs_task_definition.worker.arn

  desired_count = 0

  launch_type = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = false
  }

  tags = var.tags
}


resource "aws_appautoscaling_target" "worker" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${var.cluster_name}/${aws_ecs_service.worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}


resource "aws_appautoscaling_policy" "worker_backlog" {
  name               = "${var.project_name}-${var.worker_provider}-backlog-per-task"
  policy_type        = "TargetTrackingScaling"
  service_namespace  = aws_appautoscaling_target.worker.service_namespace
  resource_id        = aws_appautoscaling_target.worker.resource_id
  scalable_dimension = aws_appautoscaling_target.worker.scalable_dimension

  target_tracking_scaling_policy_configuration {
    target_value       = var.backlog_per_task
    scale_out_cooldown = var.scale_out_cooldown
    scale_in_cooldown  = var.scale_in_cooldown

    customized_metric_specification {
      metrics {
        id          = "backlog"
        return_data = false

        metric_stat {
          stat = "Sum"

          metric {
            namespace   = "AWS/SQS"
            metric_name = "ApproximateNumberOfMessagesVisible"

            dimensions {
              name  = "QueueName"
              value = var.queue_name
            }
          }
        }
      }

      metrics {
        id          = "running"
        return_data = false

        metric_stat {
          stat = "Average"

          metric {
            namespace   = "ECS/ContainerInsights"
            metric_name = "RunningTaskCount"

            dimensions {
              name  = "ClusterName"
              value = var.cluster_name
            }

            dimensions {
              name  = "ServiceName"
              value = aws_ecs_service.worker.name
            }
          }
        }
      }

      metrics {
        id          = "safe_running"
        return_data = false
        expression  = "FILL(running, 0)"
      }

      metrics {
        id          = "bpt"
        label       = "Backlog per task"
        expression  = "IF(safe_running > 0, backlog / safe_running, 1)"
        return_data = true
      }
    }
  }
}