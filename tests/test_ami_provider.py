import hashlib
import uuid
from cfn_ami_provider import handler


def test_with_owner_id():
    request = Request(
        "Create",
        filters={
            "name": "amzn-ami-2017.09.l-amazon-ecs-optimized",
            "owner-id": "591542846629",
        },
    )
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert response["PhysicalResourceId"].startswith("ami-")
    assert "KmsKeyIds" not in response["Data"]


def test_crud():
    request = Request(
        "Create", filters={"name": "amzn-ami-2017.09.l-amazon-ecs-optimized"}
    )
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "PhysicalResourceId" in response
    assert "KmsKeyIds" not in response["Data"]
    assert response["PhysicalResourceId"].startswith("ami-")
    physical_resource_id = response["PhysicalResourceId"]
    request = Request(
        "Update",
        filters={"name": "amzn-ami-2017.09.k-amazon-ecs-optimized"},
        physical_resource_id=physical_resource_id,
    )
    response = handler(request, {})
    assert "PhysicalResourceId" in response
    assert "KmsKeyIds" not in response["Data"]
    assert response["PhysicalResourceId"] != physical_resource_id
    request = Request(
        "Delete",
        filters={"name": "amzn-ami-2017.09.l-amazon-ecs-optimized"},
        physical_resource_id=physical_resource_id,
    )
    request = Request(
        "Delete",
        filters={"name": "amzn-ami-2017.09.k-amazon-ecs-optimized"},
        physical_resource_id=response["PhysicalResourceId"],
    )


def test_with_region():
    request = Request(
        "Create",
        filters={"name": "amzn-ami-2017.09.l-amazon-ecs-optimized"},
        region="eu-central-1",
    )
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert response["PhysicalResourceId"].startswith("ami-")
    assert "KmsKeyIds" not in response["Data"]

    request = Request(
        "Create",
        filters={"name": "amzn-ami-2017.09.l-amazon-ecs-optimized"},
        region="eu-west-1",
    )
    response2 = handler(request, {})
    assert response2["Status"] == "SUCCESS", response["Reason"]
    assert "KmsKeyIds" not in response["Data"]
    assert response2["PhysicalResourceId"].startswith("ami-")
    assert response["PhysicalResourceId"] != response2["PhysicalResourceId"]


def test_multiple():
    request = Request("Create", filters={"name": "amzn-ami-2017.09.*"})
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"].startswith("expected a single AMI, found")


def test_encrypted_ami():
    request = Request(
        "Create",
        filters={"name": "amzn2-ami-minimal-hvm-2.0.20191217.0-x86_64-ebs-encrypted"},
    )
    request["ResourceProperties"]["ExpectedNumberOfKmsKeys"] = "1"
    response = handler(request, {})
    assert response["Status"] == "SUCCESS", response["Reason"]
    assert "KmsKeyIds" in response["Data"]
    assert response["Data"]["KmsKeyIds"]
    assert response["Data"]["KmsKeyId"]


def test_encrypted_ami_key_mismatch():
    request = Request(
        "Create",
        filters={"name": "amzn2-ami-minimal-hvm-2.0.20191217.0-x86_64-ebs-encrypted"},
    )
    request["ResourceProperties"]["ExpectedNumberOfKmsKeys"] = "2"
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"] == "expected 2 kms key ids, found 1"


def test_unecrypted_ami():
    request = Request(
        "Create",
        filters={
            "name": "amzn-ami-2017.09.l-amazon-ecs-optimized",
            "owner-id": "591542846629",
        },
    )
    request["ResourceProperties"]["ExpectedNumberOfKmsKeys"] = "1"
    response = handler(request, {})
    assert response["Status"] == "FAILED", response["Reason"]
    assert response["Reason"] == "expected 1 kms key ids, found 0"


class Request(dict):
    def __init__(
        self,
        request_type,
        filters,
        owners=None,
        users=None,
        image_ids=None,
        region=None,
        physical_resource_id=None,
    ):
        self.update(
            {
                "RequestType": request_type,
                "ResponseURL": "https://httpbin.org/put",
                "StackId": "arn:aws:cloudformation:us-west-2:EXAMPLE/stack-name/guid",
                "RequestId": "request-%s" % uuid.uuid4(),
                "ResourceType": "Custom::AMI",
                "LogicalResourceId": "MyAMI",
                "ResourceProperties": {"Filters": filters},
            }
        )
        if users:
            self["ResourceProperties"]["ExecutableUsers"] = users
        if owners:
            self["ResourceProperties"]["Owners"] = owners
        if image_ids:
            self["ResourceProperties"]["Owners"] = image_ids
        if region:
            self["ResourceProperties"]["Region"] = region
        self["PhysicalResourceId"] = (
            physical_resource_id
            if physical_resource_id is not None
            else str(uuid.uuid4())
        )
