# Currency Exchange Tracking Application

## Overview

This application fetches daily exchange rates from the European Central Bank (ECB) and stores them in AWS DynamoDB. It exposes a public REST API that provides current exchange rates and their changes compared to the previous day. The project leverages AWS Lambda functions, API Gateway, and DynamoDB, packaged and deployed using AWS CloudFormation.

## AWS Services Used
- AWS Lambda
- AWS CloudFormation
- AWS API Gateway
- AWS DynamoDB
- AWS CloudWatch
- AWS S3

## Project Structure

```arduino
currency-exchange-tracker/
├── src/
│   ├── fetch_exchange_rates/
│   │   ├── __init__.py
│   │   ├── fetch_exchange_rates.py
│   ├── get_exchange_rates/
│   │   ├── __init__.py
│   │   ├── get_exchange_rates.py
│   ├── layers/
│   │   ├── requests_layer/
│   │   │   ├── python/
│   │   │   │   ├── requests/  # requests package here
│   │   │   │   ├── requests-2.25.1.dist-info/
│   │   ├── xml_layer/
│   │   │   ├── python/
│   │   │   │   ├── xmltodict/  # xmltodict package here
│   │   │   │   ├── xmltodict-0.12.0.dist-info/
├── tests/
│   ├── test_fetch_exchange_rates.py
│   ├── test_get_exchange_rates.py
├── templates/
│   ├── cloudformation.yaml
├── scripts/
│   ├── package_lambda.sh
│   ├── deploy.sh
├── README.md
├── .pre-commit-config.yaml
├── requirements.txt
├── requirements-requests.txt
├── requirements-xml.txt
└── .gitignore
```

## Setup Instructions

### Prerequisites
- AWS CLI configured with appropriate permissions
- AWS profile named `currency-exchange-tracker`

### Installing the AWS CLI

The AWS CLI is required to deploy this application. Here's a guide for installation on different operating systems:

**Windows:**

1. **Download the Installer:** Visit the AWS Command Line Interface [AWS CLI download page] and download the installer for Windows.
2. **Run the Installer:** Double-click the downloaded `.msi` file and follow the on-screen instructions.
3. **Verify Installation:** Open a Command Prompt window and type `aws --version`. If successful, the installed AWS CLI version will be displayed.

**macOS:**

1. **Install using Homebrew:** Open Terminal and run the command `brew install awscli`. Homebrew will download and install the AWS CLI for you.
2. **Verify Installation:** In Terminal, type `aws --version`. If successful, the installed AWS CLI version will be displayed.

**Linux:**

1. **Install using Package Manager:** Use your distribution's package manager (e.g., `apt`, `yum`, `dnf`) to install the AWS CLI. For example, on Ubuntu/Debian, you can use:

   ```bash
   sudo apt-get install awscli
   ```

2. **Verify Installation:** Open a Terminal window and type `aws --version`. If successful, the installed AWS CLI version will be displayed.


### Configuring AWS CLI with a New Profile

Once the AWS CLI is installed, follow these steps to configure a new profile named `currency-exchange-tracker`:

1. **Open Terminal or Command Prompt.**
2. **Run AWS Configuration:** Type the following command and press Enter:

   ```bash
   aws configure --profile currency-exchange-tracker
   ```

3. **Provide Credentials:** You will be prompted for the following information:
   - **AWS Access Key ID:** Enter the Access Key ID associated with your AWS account.
   - **AWS Secret Access Key:** Enter the Secret Access Key associated with your AWS account.
   - **Default region name:** Enter the AWS Region you want to use (e.g., `us-east-1`, `eu-west-1`).
   - **Default output format:** Choose an output format for AWS CLI commands (e.g., `json`, `text`, `table`). This determines how AWS CLI displays results.

**Example Configuration:**

The configuration process might look like this in your terminal:

```
AWS Config File Location: ~/.aws/config
AWS Access Key ID [NONE]: YOUR_ACCESS_KEY_ID
AWS Secret Access Key [NONE]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: us-east-1
Default output format [None]: json

Do you want to configure AWS SAM? (y/n) n

Success. Your AWS configuration file has been updated.
```

**Remember to replace `YOUR_ACCESS_KEY_ID` and `YOUR_SECRET_ACCESS_KEY` with your actual credentials.**

For more details on AWS CLI configuration, refer to the official documentation: [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).


### Steps

1. **Clone the Repository**
```bash
git clone <repository-url>
cd currency-exchange-tracker
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Endpoints
GET /exchange-rates: Returns current exchange rates and their changes compared to the previous day.
### Example Request
```bash
curl -X GET https://<api-id>.execute-api.<region>.amazonaws.com/prod/exchange-rates
```

### Example Response
```json
{
  "current_rates": {
    "USD": 1.2,
    "GBP": 0.85
  },
  "previous_rates": {
    "USD": 1.1,
    "GBP": 0.86
  },
  "changes": {
    "USD": 0.1,
    "GBP": -0.01
  }
}
```

### Scripts
package_lambda.sh
This script packages the Lambda functions and layers.
```bash
sh scripts/package_lambda.sh
```

deploy.sh
This script orchestrates the full deployment process.
```bash
sh scripts/deploy.sh
```

## Available Pre-commit Hooks

The pre-commit configuration in this project includes the following pre-commit hooks:

- trailing-whitespace: Checks for trailing whitespace at the end of lines.
- end-of-file-fixer: Ensures that files end with a newline character.
- check-json: Validates JSON files for syntax errors.
- check-yaml: Validates YAML files for syntax errors.
- detect-private-key: Scans for private keys accidentally committed to the repository.
- debug-statements: Detects and removes debug statements from code.
- check-added-large-files: Prevents the addition of large files to the repository.
- fix-encoding-pragma: Ensures that source files contain the correct encoding pragma.
- check-case-conflict: Checks for case conflicts in filenames on case-insensitive file systems.
- black: Enforces Python code formatting using the Black formatter.
- autoflake: Removes unused imports and variables from Python code.
- flake8: Performs code linting and static analysis.

### Installation

1. Install as git hook:
   ```bash
   pre-commit install
   ```
### Usage

1. Auto Use: when ever you try to commit then above hooks will run on changed code.
2. Manual Run:
   ```bash
   pre-commit run --all-files
   ```

## Run Test Cases

For Pytest test cases run :

```shell
PYTHONPATH=. pytest -vv -s
```

For running specific unit test case use tag name ie.

```shell
PYTHONPATH=. pytest tests/test_fetch_exchange_rates.py -vv -s
```

## CloudFormation Templates
```yaml
s3_bucket.yaml
```
This template creates an S3 bucket to store the Lambda packages.

```yaml
cloudformation.yaml
```
This template creates the DynamoDB table, Lambda functions, API Gateway, and other necessary resources.

### MIT License

This `README.md` provides detailed instructions on setting up, deploying, and using the currency exchange tracking application. It includes steps for creating necessary AWS resources, packaging and uploading Lambda functions, and deploying the CloudFormation stacks.
