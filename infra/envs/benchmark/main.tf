locals {
  lab_role_arn = "arn:aws:iam::${var.account_id}:role/LabRole"
  name_prefix  = "cs5296"
}

module "shared" {
  source       = "../../modules/shared"
  name_prefix  = local.name_prefix
  lab_role_arn = local.lab_role_arn
}

module "ec2" {
  source            = "../../modules/ec2"
  name_prefix       = local.name_prefix
  lab_role_arn      = local.lab_role_arn
  vpc_id            = module.shared.vpc_id
  public_subnet_ids = module.shared.public_subnet_ids
  app_sg_id         = module.shared.app_sg_id
  alb_target_group  = module.shared.ec2_target_group_arn
  ecr_repo_url      = module.shared.ecr_repo_url
  image_tag         = var.image_tag
  ddb_table         = module.shared.ddb_table_name
  instance_type     = var.ec2_instance_type
  min_size          = var.ec2_min_size
  max_size          = var.ec2_max_size
  region            = var.region
  instance_profile  = module.shared.instance_profile_name
}

module "fargate" {
  source           = "../../modules/fargate"
  name_prefix      = local.name_prefix
  lab_role_arn     = local.lab_role_arn
  vpc_id           = module.shared.vpc_id
  subnet_ids       = module.shared.public_subnet_ids
  app_sg_id        = module.shared.app_sg_id
  alb_target_group = module.shared.fargate_target_group_arn
  ecr_repo_url     = module.shared.ecr_repo_url
  image_tag        = var.image_tag
  ddb_table        = module.shared.ddb_table_name
  cpu              = var.fargate_cpu
  memory           = var.fargate_memory
  min_count        = var.fargate_min_count
  max_count        = var.fargate_max_count
  region           = var.region
}

module "lambda" {
  source                  = "../../modules/lambda"
  name_prefix             = local.name_prefix
  lab_role_arn            = local.lab_role_arn
  ecr_repo_url            = module.shared.ecr_repo_url
  image_tag               = var.image_tag
  ddb_table               = module.shared.ddb_table_name
  memory_mb               = var.lambda_memory_mb
  provisioned_concurrency = var.lambda_provisioned_concurrency
  alb_target_group        = module.shared.lambda_target_group_arn
}

output "ec2_url" { value = "http://${module.shared.alb_dns}/ec2" }
output "fargate_url" { value = "http://${module.shared.alb_dns}/fargate" }
output "lambda_url" { value = module.lambda.function_url }
output "lambda_alb_url" { value = "http://${module.shared.alb_dns}/lambda" }
output "ecr_repo_url" { value = module.shared.ecr_repo_url }
output "ddb_table" { value = module.shared.ddb_table_name }
