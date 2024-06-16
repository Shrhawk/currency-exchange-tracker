#!/bin/bash

# Define the S3 bucket name and AWS profile
S3_BUCKET_NAME=currency-exchange-tracker-code-bucket
AWS_PROFILE=currency-exchange-tracker

# Ensure scripts are executable
chmod +x scripts/package_lambda.sh

# Create the S3 bucket using CloudFormation
echo "Creating S3 bucket using CloudFormation..."
aws cloudformation create-stack --stack-name CurrencyExchangeS3Bucket --template-body file://./templates/s3_bucket.yaml --capabilities CAPABILITY_NAMED_IAM --profile ${AWS_PROFILE}

# Wait for the S3 bucket creation to complete
echo "Waiting for S3 bucket to be created..."
aws cloudformation wait stack-create-complete --stack-name CurrencyExchangeS3Bucket --profile ${AWS_PROFILE}

# Package Lambda functions and layers
echo "Packaging Lambda functions and layers... and upload in S3"
./scripts/package_lambda.sh


# Deploy the existing CloudFormation stack if its already created
echo "Try Deploy the existing CloudFormation stack if its already created..."
aws cloudformation update-stack --stack-name CurrencyExchangeTracker --template-body file://./templates/cloudformation.yaml --parameters ParameterKey=CodeS3BucketName,ParameterValue=${S3_BUCKET_NAME} --capabilities CAPABILITY_NAMED_IAM --profile ${AWS_PROFILE}

echo "Waiting for the stack to be created..."
aws cloudformation wait stack-update-complete --stack-name CurrencyExchangeTracker --profile ${AWS_PROFILE}

# Deploy the rest of the CloudFormation stack
echo "Create and Deploy new CloudFormation stack..."
aws cloudformation create-stack --stack-name CurrencyExchangeTracker --template-body file://./templates/cloudformation.yaml --parameters ParameterKey=CodeS3BucketName,ParameterValue=${S3_BUCKET_NAME} --capabilities CAPABILITY_NAMED_IAM --profile ${AWS_PROFILE}

echo "Waiting for the stack to be created..."
aws cloudformation wait stack-create-complete --stack-name CurrencyExchangeTracker --profile ${AWS_PROFILE}

echo "Deployment complete. You can access the API using the following URL:"
API_URL=$(aws cloudformation describe-stacks --stack-name CurrencyExchangeTracker --query "Stacks[0].Outputs[?OutputKey=='ApiGatewayUrl'].OutputValue" --output text --profile ${AWS_PROFILE})
echo "${API_URL}"
