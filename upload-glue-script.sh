#!/bin/bash

# Set your bucket name
BUCKET="my-prod-glue-bucket"

# Set local job directory and remote prefix
LOCAL_DIR="./glue-jobs"
REMOTE_PREFIX="glue-scripts"

echo "🚀 Uploading all Glue scripts from $LOCAL_DIR to s3://$BUCKET/$REMOTE_PREFIX/"

# Loop over all .py files in the glue-jobs/ directory
for file in "$LOCAL_DIR"/*.py; do
  if [ -f "$file" ]; then
    filename=$(basename "$file")
    aws s3 cp "$file" "s3://$BUCKET/$REMOTE_PREFIX/$filename"
    echo "✅ Uploaded $filename"
  fi
done

# Create the glue-temp/ directory if it doesn't exist
aws s3api put-object --bucket "$BUCKET" --key glue-temp/
echo "📁 Ensured s3://$BUCKET/glue-temp/ exists"

echo "🎉 All scripts uploaded."
