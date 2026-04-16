data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

locals {
  user_data = <<-EOT
    #!/bin/bash
    set -euo pipefail
    dnf install -y docker awscli
    systemctl enable --now docker

    REGION=${var.region}
    IMAGE=${var.ecr_repo_url}:${var.image_tag}

    aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin ${var.ecr_repo_url}
    docker pull "$IMAGE"

    docker run -d --name shortlink --restart always \
      -p 8080:8080 \
      -e PLATFORM=ec2 \
      -e DDB_TABLE=${var.ddb_table} \
      -e AWS_REGION=${var.region} \
      "$IMAGE"
  EOT
}

resource "aws_launch_template" "app" {
  name_prefix   = "${var.name_prefix}-ec2-"
  image_id      = data.aws_ami.al2023.id
  instance_type = var.instance_type

  iam_instance_profile {
    name = var.instance_profile
  }

  vpc_security_group_ids = [var.app_sg_id]

  user_data = base64encode(local.user_data)

  tag_specifications {
    resource_type = "instance"
    tags = {
      Name = "${var.name_prefix}-ec2"
    }
  }
}

resource "aws_autoscaling_group" "app" {
  name                      = "${var.name_prefix}-ec2-asg"
  max_size                  = var.max_size
  min_size                  = var.min_size
  desired_capacity          = var.min_size
  vpc_zone_identifier       = var.public_subnet_ids
  health_check_type         = "ELB"
  health_check_grace_period = 120
  target_group_arns         = [var.alb_target_group]

  launch_template {
    id      = aws_launch_template.app.id
    version = "$Latest"
  }

  instance_refresh {
    strategy = "Rolling"
    preferences { min_healthy_percentage = 50 }
  }

  tag {
    key                 = "Name"
    value               = "${var.name_prefix}-ec2"
    propagate_at_launch = true
  }
}

resource "aws_autoscaling_policy" "cpu_target" {
  name                   = "${var.name_prefix}-ec2-cpu50"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 50.0
  }
}
