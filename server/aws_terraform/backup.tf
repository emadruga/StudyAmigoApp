# =============================================================================
# StudyAmigo - S3 Backup Bucket + IAM for EC2 Instance Profile
# =============================================================================
# Provisions:
#   - S3 bucket for database backups (encrypted, private, lifecycle-protected)
#   - IAM role + scoped S3 policy for the EC2 instance
#   - IAM instance profile to attach the role to the EC2 instance
#
# Rotation is handled entirely by backup.sh (4-week, 28-slot scheme).
# No S3 lifecycle rules are needed — old slots are overwritten, not deleted.
# =============================================================================

# Resolve account ID so bucket names are globally unique
data "aws_caller_identity" "current" {}

locals {
  # e.g. study-amigo-backups-123456789012
  backup_bucket_name = "${var.project_name}-backups-${data.aws_caller_identity.current.account_id}"
}

# -----------------------------------------------------------------------------
# S3 Bucket
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "backups" {
  bucket = local.backup_bucket_name

  # Intentionally NOT force_destroy — protect data from accidental `terraform destroy`
  force_destroy = false

  tags = {
    Name = "${var.project_name}-backups"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {
  bucket = aws_s3_bucket.backups.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "backups" {
  bucket                  = aws_s3_bucket.backups.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning disabled — backup.sh manages the 28-slot rotation by overwriting
resource "aws_s3_bucket_versioning" "backups" {
  bucket = aws_s3_bucket.backups.id
  versioning_configuration {
    status = "Disabled"
  }
}

# -----------------------------------------------------------------------------
# IAM Role — assumed by EC2 via the instance profile
# -----------------------------------------------------------------------------
resource "aws_iam_role" "ec2_backup" {
  name        = "${var.project_name}-ec2-backup-role"
  description = "Allows the StudyAmigo EC2 instance to read/write its S3 backup bucket"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "${var.project_name}-ec2-backup-role"
  }
}

# Scoped policy: only the backup bucket, only the actions needed
resource "aws_iam_role_policy" "ec2_backup_s3" {
  name = "${var.project_name}-s3-backup-policy"
  role = aws_iam_role.ec2_backup.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowBucketList"
        Effect = "Allow"
        Action = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.backups.arn]
      },
      {
        Sid    = "AllowObjectReadWrite"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject"
        ]
        Resource = ["${aws_s3_bucket.backups.arn}/*"]
      }
    ]
  })
}

# -----------------------------------------------------------------------------
# IAM Instance Profile — wrapper that attaches the role to an EC2 instance
# -----------------------------------------------------------------------------
resource "aws_iam_instance_profile" "ec2_backup" {
  name = "${var.project_name}-ec2-instance-profile"
  role = aws_iam_role.ec2_backup.name

  tags = {
    Name = "${var.project_name}-ec2-instance-profile"
  }
}
