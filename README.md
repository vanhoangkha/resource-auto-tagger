# Resource Auto Tagger

Automatically tags new EC2 instances and attached EBS volumes based on IAM identity.

## Architecture

```
EC2 RunInstances → CloudTrail → EventBridge → Lambda → EC2/EBS Tags
```

## Quick Deploy

```bash
sam build
sam deploy --parameter-overrides AlertEmail=your@email.com
```

## Tag Sources

| Source | Path/Location |
|--------|---------------|
| IAM User Tags | Tags on the IAM user |
| IAM Role Tags | Tags on the assumed role |
| SSM Parameters | `/auto-tag/{identity}/tag/{key}` |

## Auto-Applied Tags

- `IAM User Name` or `IAM Role Name`
- `Date created`
- `Created by` (for assumed roles)
- All tags from IAM identity
- All tags from SSM parameters

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
| Lambda Function | Processes CloudTrail events |
| EventBridge Rule | Triggers on RunInstances |
| SQS DLQ | Captures failed invocations |
| CloudWatch Alarm | Alerts on errors |
| SNS Topic | Email notifications (optional) |

## Best Practices

- ✅ Least privilege IAM
- ✅ Reserved concurrency (10)
- ✅ X-Ray tracing
- ✅ Dead Letter Queue
- ✅ 30-day log retention
- ✅ Error alerting

## Prerequisites

- AWS SAM CLI
- CloudTrail enabled in your account

## License

MIT-0
