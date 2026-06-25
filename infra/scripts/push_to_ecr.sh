#!/bin/bash
set -euo pipefail
AWS_REGION=${AWS_REGION:-us-east-1}
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/nexus-backend"

aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

docker build -t nexus-backend ./backend
docker tag nexus-backend:latest "$ECR_URI:latest"
docker tag nexus-backend:latest "$ECR_URI:$(git rev-parse --short HEAD)"
docker push "$ECR_URI:latest"
docker push "$ECR_URI:$(git rev-parse --short HEAD)"
echo "Pushed: $ECR_URI:$(git rev-parse --short HEAD)"
