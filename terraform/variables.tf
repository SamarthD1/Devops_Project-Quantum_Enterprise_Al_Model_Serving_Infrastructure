variable "aws_region" {
  description = "Target AWS region for deploying infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "Name of the EKS cluster for Project Quantum"
  type        = string
  default     = "quantum-eks-cluster"
}

variable "environment" {
  description = "Deployment environment stage"
  type        = string
  default     = "production"
}

variable "instance_types" {
  description = "EC2 instance types for the EKS node group"
  type        = list(string)
  default     = ["t3.medium"]
}
