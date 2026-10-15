variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-south-1"
}

variable "project" {
  description = "Name prefix for resources"
  type        = string
  default     = "clinicflow"
}

variable "environment" {
  description = "Environment tag (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.20.0.0/16"
}

variable "kubernetes_version" {
  description = "EKS control plane version (keep within standard support to avoid extended-support fees)"
  type        = string
  default     = "1.34"
}

variable "node_instance_types" {
  description = "Instance types for the managed node group (c7i-flex.large is allowed on the AWS Free plan, t3.medium is not)"
  type        = list(string)
  default     = ["c7i-flex.large"]
}

variable "node_desired_size" {
  type    = number
  default = 2
}

variable "node_min_size" {
  type    = number
  default = 1
}

variable "node_max_size" {
  type    = number
  default = 3
}
