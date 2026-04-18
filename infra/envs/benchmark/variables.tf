variable "region" {
  type    = string
  default = "us-east-1"
}

variable "owner_tag" {
  type    = string
  default = "cs5296-group"
}

variable "image_tag" {
  description = "Image tag pushed to the ECR repo from app/"
  type        = string
  default     = "v1"
}

variable "ec2_instance_type" {
  type    = string
  default = "t3.small"
}

variable "ec2_min_size" {
  type    = number
  default = 1
}

variable "ec2_max_size" {
  type    = number
  default = 6
}

variable "fargate_cpu" {
  type    = number
  default = 512
}

variable "fargate_memory" {
  type    = number
  default = 1024
}

variable "fargate_min_count" {
  type    = number
  default = 1
}

variable "fargate_max_count" {
  type    = number
  default = 10
}

variable "lambda_memory_mb" {
  type    = number
  default = 1024
}

variable "lambda_provisioned_concurrency" {
  type    = number
  default = 0
}

variable "lambda_reserved_concurrency" {
  type        = number
  default     = 50
  description = "Reserved concurrency cap for the Lambda function, limits peak fan-out"
}
