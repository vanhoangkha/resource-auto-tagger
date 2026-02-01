# Resource Auto Tagger

Automatically tags new EC2 instances and attached EBS volumes based on IAM identity.

## Architecture

```
EC2 RunInstances → CloudTrail → EventBridge → Lambda → EC2/EBS Tags
```

## Quick Deploy

```bash
# Install SAM CLI first: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

sam build
sam deploy --guided

# Or with email alerts:
sam deploy --parameter-overrides AlertEmail=your@email.com
```

## Tag Sources

| Source | Path/Location |
|--------|---------------|
| IAM User Tags | Tags on the IAM user |
| IAM Role Tags | Tags on the assumed role |
| SSM Parameters | `/auto-tag/{identity}/tag/{key}` |

## Auto-Applied Tags

| Tag | Description |
|-----|-------------|
| `IAM User Name` | IAM user who created the instance |
| `IAM Role Name` | Assumed role used to create instance |
| `Created by` | User ID who assumed the role |
| `Date created` | Timestamp of instance creation |
| + IAM tags | All tags from IAM user/role |
| + SSM tags | All tags from SSM parameters |

## SSM Parameter Examples

```bash
# For IAM user "john"
aws ssm put-parameter --name "/auto-tag/john/tag/Project" --value "MyProject" --type String

# For role "developer" with user "jane"
aws ssm put-parameter --name "/auto-tag/developer/jane/tag/Team" --value "Backend" --type String
```

## Resources Created

| Resource | Description |
|----------|-------------|
| Lambda Function | Processes CloudTrail events (ARM64, Python 3.12) |
| EventBridge Rule | Triggers on RunInstances API calls |
| SQS DLQ | Captures failed invocations (encrypted) |
| CloudWatch Logs | 30-day retention |
| CloudWatch Alarm | Alerts on errors |
| SNS Topic | Email notifications (optional, encrypted) |

## Best Practices

- ✅ Least privilege IAM (resource-scoped)
- ✅ ARM64 architecture (cost optimized)
- ✅ Reserved concurrency (10)
- ✅ X-Ray tracing enabled
- ✅ Dead Letter Queue with encryption
- ✅ 30-day log retention
- ✅ CloudWatch error alerting
- ✅ SNS encryption at rest
- ✅ Configurable log level
- ✅ Structured logging

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `AlertEmail` | (none) | Email for error notifications |
| `LogLevel` | INFO | DEBUG, INFO, WARNING, ERROR |

## Prerequisites

- AWS SAM CLI
- CloudTrail enabled in your account
- Python 3.12

## Cleanup

```bash
sam delete --stack-name resource-auto-tagger
```

## License

MIT-0
