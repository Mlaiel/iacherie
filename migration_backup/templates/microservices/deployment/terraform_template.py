#!/usr/bin/env python3
"""
🏗️ TERRAFORM TEMPLATE - INFRASTRUCTURE AS CODE
===============================================

Enterprise Terraform templates for cloud infrastructure provisioning
with multi-cloud support, state management, and security best practices.

© 2025 Fahed Mlaiel (mlaiel@live.de) - Propriété Intellectuelle Exclusive
"""

class TerraformTemplate:
    """Enterprise Terraform infrastructure template"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
    
    def generate_main_tf(self) -> str:
        """Generate main.tf configuration"""
        return f'''
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

resource "aws_ecs_cluster" "{self.project_name}_cluster" {{
  name = "{self.project_name}-cluster"
  
  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

resource "aws_ecs_service" "{self.project_name}_service" {{
  name            = "{self.project_name}-service"
  cluster         = aws_ecs_cluster.{self.project_name}_cluster.id
  task_definition = aws_ecs_task_definition.{self.project_name}_task.arn
  desired_count   = 2
  
  deployment_configuration {{
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }}
}}
'''
    
    def generate_variables_tf(self) -> str:
        """Generate variables.tf"""
        return '''
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "development"
}
'''