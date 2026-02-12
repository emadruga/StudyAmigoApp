# =============================================================================
# StudyAmigo - Terraform Outputs
# =============================================================================

output "instance_id" {
  description = "EC2 instance ID"
  value       = aws_instance.study_amigo.id
}

output "public_ip" {
  description = "Instance public IP (changes on stop/start - use elastic_ip instead)"
  value       = aws_instance.study_amigo.public_ip
}

output "elastic_ip" {
  description = "Elastic IP (static) - use this for Cloudflare DNS A record"
  value       = aws_eip.study_amigo.public_ip
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ${replace(var.ssh_public_key_path, ".pub", "")} ubuntu@${aws_eip.study_amigo.public_ip}"
}

output "app_url" {
  description = "Application URL (available after Cloudflare DNS is configured)"
  value       = "https://${var.domain_name}"
}

output "ami_id" {
  description = "AMI ID used for the instance (useful for Reserved Instance matching)"
  value       = data.aws_ami.ubuntu.id
}
