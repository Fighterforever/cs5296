output "function_name" { value = aws_lambda_function.app.function_name }
output "function_arn" { value = aws_lambda_function.app.arn }
output "alias_arn" { value = aws_lambda_alias.live.arn }
