output "eks_cluster_endpoint" {
  description = "Connection API endpoint for EKS control plane"
  value       = aws_eks_cluster.eks.endpoint
}

output "eks_cluster_name" {
  description = "EKS cluster identifier"
  value       = aws_eks_cluster.eks.name
}

output "vpc_id" {
  description = "ID of the provisioned AWS VPC"
  value       = aws_vpc.quantum_vpc.id
}

output "kubeconfig_update_command" {
  description = "CLI helper command to configure local kubeconfig connection to EKS"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.eks.name}"
}
