#!/bin/bash

# Check if stack name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <STACK_NAME>"
  exit 1
fi

STACK_NAME="$1"

# Dynamically retrieve bucket name from CloudFormation parameters
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Parameters[?ParameterKey=='SiteBucketName'].ParameterValue" \
    --output text)

# Dynamically retrieve API Endpoint from CloudFormation outputs
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)

echo "Deploying stack: $STACK_NAME"
echo "Deploying to bucket: $BUCKET_NAME"
echo "Injecting API endpoint: $API_ENDPOINT"

# Prepare temporary deployment folder
mkdir -p deploy_tmp

# Inject API endpoint into index.html
sed "s|{{API_ENDPOINT}}|${API_ENDPOINT}|g" frontend/index.html > deploy_tmp/index.html

# Copy everything except index.html
for file in frontend/*; do
  if [[ "$(basename "$file")" != "index.html" ]]; then
    cp -r "$file" deploy_tmp/
  fi
done

# Sync to S3
aws s3 sync deploy_tmp "s3://$BUCKET_NAME/" --delete

# Clean up
rm -rf deploy_tmp

echo "Frontend deployed successfully!"
