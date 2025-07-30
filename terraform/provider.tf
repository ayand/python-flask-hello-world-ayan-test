provider "aws" {
  region = "us-east-1"
}
terraform {
  backend "s3" {
    bucket  = "terraform-backend-396008559107"
    key     = "global/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}