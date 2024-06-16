#!/bin/bash

# Define the S3 bucket name and AWS profile
S3_BUCKET_NAME=currency-exchange-tracker-code-bucket
AWS_PROFILE=currency-exchange-tracker

# Function to create and zip a layer
create_layer() {
  local layer_name=$1
  local requirements_file=$2

  mkdir -p src/layers/${layer_name}/python
  pip install -r ${requirements_file} -t src/layers/${layer_name}/python
  cd src/layers/${layer_name}
  zip -r ${layer_name}.zip python
  mv ${layer_name}.zip ../../../
  cd ../../../
}

# Package fetch_exchange_rates
cd src/fetch_exchange_rates
zip -r ../../fetch_exchange_rates.zip .
cd ../../

# Package get_exchange_rates
cd src/get_exchange_rates
zip -r ../../get_exchange_rates.zip .
cd ../../

# Create and package requests layer
create_layer "requests_layer" "requirements-requests.txt"

# Create and package xml layer
create_layer "xml_layer" "requirements-xml.txt"

# Upload packages to S3 using the specified AWS profile
aws s3 cp fetch_exchange_rates.zip s3://${S3_BUCKET_NAME}/ --profile ${AWS_PROFILE}
aws s3 cp get_exchange_rates.zip s3://${S3_BUCKET_NAME}/ --profile ${AWS_PROFILE}
aws s3 cp requests_layer.zip s3://${S3_BUCKET_NAME}/ --profile ${AWS_PROFILE}
aws s3 cp xml_layer.zip s3://${S3_BUCKET_NAME}/ --profile ${AWS_PROFILE}

echo "Packages have been created and uploaded to S3 using profile ${AWS_PROFILE}."
