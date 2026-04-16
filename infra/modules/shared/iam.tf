# Learner Lab disallows IAM role creation. We look up the pre-supplied
# instance profile for LabRole and expose it to the EC2 module.
data "aws_iam_instance_profile" "lab" {
  name = "LabInstanceProfile"
}
