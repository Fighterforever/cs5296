resource "aws_lb" "main" {
  name               = "${var.name_prefix}-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids
  idle_timeout       = 60
}

resource "aws_lb_target_group" "ec2" {
  name        = "${var.name_prefix}-ec2-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "instance"

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 15
    timeout             = 5
    matcher             = "200"
  }
}

resource "aws_lb_target_group" "fargate" {
  name        = "${var.name_prefix}-fg-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/healthz"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 15
    timeout             = 5
    matcher             = "200"
  }
}

resource "aws_lb_target_group" "lambda" {
  name        = "${var.name_prefix}-lb-tg"
  target_type = "lambda"
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "fixed-response"
    fixed_response {
      content_type = "text/plain"
      message_body = "use /ec2 /fargate /lambda"
      status_code  = "404"
    }
  }
}

resource "aws_lb_listener_rule" "ec2" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 10
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ec2.arn
  }
  condition {
    path_pattern { values = ["/ec2/*", "/ec2"] }
  }
}

resource "aws_lb_listener_rule" "fargate" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 20
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.fargate.arn
  }
  condition {
    path_pattern { values = ["/fargate/*", "/fargate"] }
  }
}

resource "aws_lb_listener_rule" "lambda" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 30
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.lambda.arn
  }
  condition {
    path_pattern { values = ["/lambda/*", "/lambda"] }
  }
}
