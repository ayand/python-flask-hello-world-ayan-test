#!/bin/sh 

ecr_repo="flask-docker-app-ayan"
aws_account_id=$(aws sts get-caller-identity --query Account --output text)
region=$(aws configure get region)
# login and create ecr repository 
aws ecr create-repository --repository-name ${ecr_repo} --image-scanning-configuration scanOnPush=true --region ${region}
aws ecr get-login-password --region ${region} | docker login --username AWS --password-stdin ${aws_account_id}.dkr.ecr.${region}.amazonaws.com
docker build -t flask-python-app .
docker tag flask-python-app:latest ${aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/${ecr_repo}:latest
docker push ${aws_account_id}.dkr.ecr.us-east-1.amazonaws.com/${ecr_repo}:latest