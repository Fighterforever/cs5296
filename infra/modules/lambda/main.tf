resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.name_prefix}-shortlink"
  retention_in_days = 7
}

resource "aws_lambda_function" "app" {
  function_name                  = "${var.name_prefix}-shortlink"
  role                           = var.exec_role_arn
  package_type                   = "Image"
  image_uri                      = "${var.ecr_repo_url}:${var.image_tag}"
  memory_size                    = var.memory_mb
  timeout                        = 30
  architectures                  = ["x86_64"]
  publish                        = true
  reserved_concurrent_executions = var.reserved_concurrency

  environment {
    variables = {
      PLATFORM    = "lambda"
      PATH_PREFIX = "/lambda"
      DDB_TABLE   = var.ddb_table
    }
  }

  depends_on = [aws_cloudwatch_log_group.lambda]
}

resource "aws_lambda_alias" "live" {
  name             = "live"
  function_name    = aws_lambda_function.app.function_name
  function_version = aws_lambda_function.app.version
}

resource "aws_lambda_provisioned_concurrency_config" "live" {
  count                             = var.provisioned_concurrency > 0 ? 1 : 0
  function_name                     = aws_lambda_function.app.function_name
  qualifier                         = aws_lambda_alias.live.name
  provisioned_concurrent_executions = var.provisioned_concurrency
}

resource "aws_lambda_permission" "alb" {
  statement_id  = "AllowALB"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.app.function_name
  qualifier     = aws_lambda_alias.live.name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = var.alb_target_group
}

resource "aws_lb_target_group_attachment" "lambda" {
  target_group_arn = var.alb_target_group
  target_id        = aws_lambda_alias.live.arn
  depends_on       = [aws_lambda_permission.alb]
}
