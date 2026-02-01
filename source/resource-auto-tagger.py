"""AWS Lambda resource tagger for new Amazon EC2 instances & attached EBS volumes.

Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

# Configure structured logging
log = logging.getLogger(__name__)
log.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# Initialize clients outside handler for connection reuse
iam_client = boto3.client("iam")
ssm_client = boto3.client("ssm")
ec2_client = boto3.client("ec2")


def get_iam_role_tags(role_name: str) -> list | None:
    """Get resource tags assigned to an IAM role."""
    try:
        return iam_client.list_role_tags(RoleName=role_name).get("Tags")
    except ClientError as e:
        log.error(f"Failed to get role tags: {e}")
        return None


def get_iam_user_tags(user_name: str) -> list | None:
    """Get resource tags assigned to an IAM user."""
    try:
        return iam_client.list_user_tags(UserName=user_name).get("Tags")
    except ClientError as e:
        log.error(f"Failed to get user tags: {e}")
        return None


def get_ssm_parameter_tags(iam_user_name: str = None, role_name: str = None, user_id: str = None) -> list | None:
    """Get resource tags from SSM Parameter Store."""
    if iam_user_name:
        path = f"/auto-tag/{iam_user_name}/tag"
    elif role_name and user_id:
        path = f"/auto-tag/{role_name}/{user_id}/tag"
    else:
        return None

    try:
        response = ssm_client.get_parameters_by_path(Path=path, Recursive=True, WithDecryption=True)
        params = response.get("Parameters", [])
        return [{"Key": p["Name"].split("/")[-1], "Value": p["Value"]} for p in params] or None
    except ClientError as e:
        log.error(f"Failed to get SSM parameters: {e}")
        return None


def apply_tags(instance_id: str, tags: list) -> bool:
    """Apply tags to EC2 instance and attached EBS volumes."""
    if not tags:
        return True

    try:
        # Tag instance
        ec2_client.create_tags(Resources=[instance_id], Tags=tags)

        # Tag attached volumes
        volumes = ec2_client.describe_volumes(
            Filters=[{"Name": "attachment.instance-id", "Values": [instance_id]}]
        ).get("Volumes", [])

        volume_ids = [v["VolumeId"] for v in volumes]
        if volume_ids:
            ec2_client.create_tags(Resources=volume_ids, Tags=tags)

        return True
    except ClientError as e:
        log.error(f"Failed to apply tags to {instance_id}: {e}")
        return False


def parse_event(event: dict) -> dict:
    """Extract relevant fields from CloudTrail event."""
    detail = event.get("detail", {})
    user_identity = detail.get("userIdentity", {})
    result = {
        "instances": detail.get("responseElements", {}).get("instancesSet", {}).get("items", []),
        "event_time": detail.get("eventTime"),
    }

    if user_identity.get("type") == "IAMUser":
        result["iam_user_name"] = user_identity.get("userName")
    elif user_identity.get("type") == "AssumedRole":
        session = user_identity.get("sessionContext", {}).get("sessionIssuer", {})
        if session.get("type") == "Role":
            result["role_name"] = session.get("arn", "").split("/")[-1]
            result["user_id"] = user_identity.get("arn", "").split("/")[-1]

    return result


def lambda_handler(event: dict, context) -> dict:
    """Main Lambda handler."""
    parsed = parse_event(event)
    tags = []

    # Add identity tags
    if parsed.get("iam_user_name"):
        tags.append({"Key": "IAM User Name", "Value": parsed["iam_user_name"]})
        tags.extend(get_iam_user_tags(parsed["iam_user_name"]) or [])
        tags.extend(get_ssm_parameter_tags(iam_user_name=parsed["iam_user_name"]) or [])

    if parsed.get("role_name"):
        tags.append({"Key": "IAM Role Name", "Value": parsed["role_name"]})
        tags.extend(get_iam_role_tags(parsed["role_name"]) or [])
        if parsed.get("user_id"):
            tags.append({"Key": "Created by", "Value": parsed["user_id"]})
            tags.extend(get_ssm_parameter_tags(role_name=parsed["role_name"], user_id=parsed["user_id"]) or [])

    if parsed.get("event_time"):
        tags.append({"Key": "Date created", "Value": parsed["event_time"]})

    # Apply tags to instances
    success_count = 0
    for item in parsed.get("instances", []):
        instance_id = item.get("instanceId")
        if apply_tags(instance_id, tags):
            log.info(f"Tagged {instance_id}: {json.dumps(tags)}")
            success_count += 1
        else:
            log.error(f"Failed to tag {instance_id}")

    return {"statusCode": 200, "tagged": success_count, "total": len(parsed.get("instances", []))}
