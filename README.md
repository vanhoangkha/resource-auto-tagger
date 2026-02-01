# AWS Resource Auto Tagger

Automatically tag EC2 instances and EBS volumes based on IAM identity using AWS Lambda, EventBridge, and CloudTrail.

## Overview

Resource Auto Tagger solves the challenge of tracking AWS resource ownership by automatically applying tags when EC2 instances are launched. Tags are pulled from IAM users, IAM roles, and SSM Parameter Store.

### Key Features

- **Zero manual tagging** - Tags applied automatically on instance launch
- **Multiple tag sources** - IAM user tags, role tags, and SSM parameters
- **EBS volume support** - Attached volumes tagged alongside instances
- **Cost optimized** - ARM64 Lambda with reserved concurrency
- **Production ready** - DLQ, X-Ray tracing, CloudWatch alarms

## Architecture

```
EC2 RunInstances → CloudTrail → EventBridge → Lambda → EC2/EBS Tags
```

## Quick Start

### Prerequisites

- AWS SAM CLI ([Install Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html))
- CloudTrail enabled in your account
- Python 3.12

### Deploy

```bash
git clone https://github.com/vanhoangkha/resource-auto-tagger.git
cd resource-auto-tagger
sam build
sam deploy --guided
```

With email alerts:
```bash
sam deploy --parameter-overrides AlertEmail=your@email.com
```

## How It Works

### Auto-Applied Tags

| Tag | Description |
|-----|-------------|
| `IAM User Name` | IAM user who created the instance |
| `IAM Role Name` | Assumed role used to create instance |
| `Created by` | User ID who assumed the role |
| `Date created` | Timestamp of instance creation |

Plus all tags from:
- IAM user/role resource tags
- SSM Parameter Store

### Tag Sources

| Source | Location |
|--------|----------|
| IAM User Tags | Tags on the IAM user |
| IAM Role Tags | Tags on the assumed role |
| SSM Parameters | `/auto-tag/{identity}/tag/{key}` |

### SSM Parameter Examples

```bash
# Tag for IAM user "john"
aws ssm put-parameter --name "/auto-tag/john/tag/Project" --value "MyProject" --type String

# Tag for role "developer" with user "jane"
aws ssm put-parameter --name "/auto-tag/developer/jane/tag/Team" --value "Backend" --type String
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `AlertEmail` | (none) | Email for error notifications |
| `LogLevel` | INFO | DEBUG, INFO, WARNING, ERROR |

## Resources Created

| Resource | Description |
|----------|-------------|
| Lambda Function | Processes CloudTrail events (ARM64, Python 3.12) |
| EventBridge Rule | Triggers on RunInstances API calls |
| SQS Dead Letter Queue | Captures failed invocations |
| CloudWatch Log Group | 30-day retention |
| CloudWatch Alarm | Alerts on errors |
| SNS Topic | Email notifications (optional) |

## Security

- Least privilege IAM policies
- Resource-scoped permissions
- SQS encryption enabled
- SNS encryption at rest
- No hardcoded credentials

## Cleanup

```bash
sam delete --stack-name resource-auto-tagger
```

## License

MIT-0 - See [LICENSE](LICENSE)

## Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for guidelines.
