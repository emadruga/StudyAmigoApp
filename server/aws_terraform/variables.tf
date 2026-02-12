# =============================================================================
# StudyAmigo - Terraform Variables
# =============================================================================

variable "project_name" {
  description = "Project name used for tagging and naming AWS resources"
  type        = string
  default     = "study-amigo"
}

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 instance type. t4g.micro is the cheapest ARM option (2 vCPU, 1GB RAM)"
  type        = string
  default     = "t4g.micro"
}

variable "ebs_volume_size" {
  description = "Root EBS volume size in GB. 20GB is sufficient for the OS, Docker images, and SQLite databases"
  type        = number
  default     = 20
}

variable "ssh_public_key_path" {
  description = "Path to your SSH public key file (e.g., ~/.ssh/study-amigo-aws.pub)"
  type        = string
}

variable "ssh_allowed_cidrs" {
  description = "List of CIDR blocks allowed to SSH into the instance. Use [\"0.0.0.0/0\"] to allow from anywhere, or restrict to your IP (e.g., [\"203.0.113.50/32\"])"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "flask_secret_key" {
  description = "Secret key for Flask session management. Generate with: python3 -c 'import secrets; print(secrets.token_hex(24))'"
  type        = string
  sensitive   = true
}

variable "git_repo_url" {
  description = "Public Git repository URL to clone on the EC2 instance"
  type        = string
  default     = "https://github.com/emadruga/StudyAmigoApp.git"
}

variable "domain_name" {
  description = "The domain name for the application (used in CORS configuration)"
  type        = string
  default     = "study-amigo.app"
}
