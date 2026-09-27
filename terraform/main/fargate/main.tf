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


resource "aws_appautoscaling_policy" "worker_scale_out" {
  name               = "${var.project_name}-${var.worker_provider}-scale-out"
  policy_type        = "StepScaling"
  service_namespace  = "ecs"
  resource_id        = "service/${var.cluster_name}/${aws_ecs_service.worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"

  step_scaling_policy_configuration {
    adjustment_type         = "ChangeInCapacity"
    cooldown                = var.scale_out_cooldown
    metric_aggregation_type = "Average"

    step_adjustment {
      metric_interval_lower_bound = 0
      scaling_adjustment           = var.scale_out_step_1
    }

    step_adjustment {
      metric_interval_lower_bound = 10
      scaling_adjustment           = var.scale_out_step_2
    }

    step_adjustment {
      metric_interval_lower_bound = 20
      scaling_adjustment           = var.scale_out_step_3
    }
  }
}