variable "project_name" {
  type = string
}

variable "tags" {
  type = list(string)
}

variable "queue_name" {
  type = string
}

variable "autoscaling_policy_arn" {
  type = string
}

variable "queue_depth_threshold"{
    type = int
}
