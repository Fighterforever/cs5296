variable "name_prefix" { type = string }
variable "lab_role_arn" { type = string }
variable "ecr_repo_url" { type = string }
variable "image_tag" { type = string }
variable "ddb_table" { type = string }
variable "memory_mb" { type = number }
variable "provisioned_concurrency" { type = number }
variable "alb_target_group" { type = string }
