# Resource Auto Tagger

Automatically tags new EC2 instances and attached EBS volumes based on IAM identity.

## Architecture

```
EC2 RunInstances → CloudTrail → EventBridge → Lambda → EC2/EBS Tags
```

## Deployed Resources

| Resource | Name |
|----------|------|
| Lambda | `resource-auto-tagger` |
| IAM Role | `resource-auto-tagger-role` |
| EventBridge Rule | `resource-auto-tagger-rule` |
| Dead Letter Queue | `resource-auto-tagger-dlq` |
| SNS Topic | `resource-auto-tagger-alerts` |
| CloudWatch Alarm | `resource-auto-tagger-errors` |

## Tag Sources

1. **IAM User Tags** - Tags assigned to the IAM user creating the instance
2. **IAM Role Tags** - Tags assigned to the assumed role
3. **SSM Parameters** - Custom tags stored at `/auto-tag/{identity}/tag/{key}`

## Auto-Applied Tags

- `IAM User Name` or `IAM Role Name`
- `Date created`
- `Created by` (for assumed roles)
- All tags from IAM identity
- All tags from SSM parameters

## SSM Parameter Format

```
/auto-tag/{user-name}/tag/{tag-key}          # For IAM users
/auto-tag/{role-name}/{user-id}/tag/{tag-key} # For assumed roles
```

## Best Practices Applied

- ✅ Least privilege IAM permissions
- ✅ Reserved concurrency (10)
- ✅ X-Ray tracing enabled
- ✅ Dead Letter Queue for failures
- ✅ 30-day log retention
- ✅ CloudWatch alarm with email alerts

## License

MIT-0 License
