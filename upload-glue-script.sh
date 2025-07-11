#!/bin/bash

set -e

# Get values from GitHub Actions environment
ENVIRONMENT=${ENV_SUFFIX:-dev}
REGION=${AWS_REGION:-us-east-2}
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET="glue-scripts-${ENVIRONMENT}-${ACCOUNT_ID}-${REGION}"


# Set local directory and remote prefix
LOCAL_DIR="./glue-jobs"
REMOTE_PREFIX="glue-scripts"

echo "🚀 Uploading all Glue scripts from $LOCAL_DIR to s3://$BUCKET/$REMOTE_PREFIX/"

for file in "$LOCAL_DIR"/*.py; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    aws s3 cp "$file" "s3://$BUCKET/$REMOTE_PREFIX/$filename" --region "$REGION"
    echo "✅ Uploaded $filename"
  fi
done

# Ensure glue-temp/ directory exists in S3
aws s3api put-object --bucket "$BUCKET" --key glue-temp/ --region "$REGION"
echo "📁 Ensured s3://$BUCKET/glue-temp/ exists"

echo "🎉 All scripts uploaded to $BUCKET."
