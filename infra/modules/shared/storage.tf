resource "aws_ecr_repository" "app" {
  name                 = "${var.name_prefix}-shortlink"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "aws_dynamodb_table" "links" {
  name         = "${var.name_prefix}-shortlink"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "code"

  attribute {
    name = "code"
    type = "S"
  }

  point_in_time_recovery {
    enabled = false
  }
}
