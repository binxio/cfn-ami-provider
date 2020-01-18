import os
import logging
import boto3
from cfn_resource_provider import ResourceProvider

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger()

request_schema = {
    "type": "object",
    "required": ["Filters"],
    "properties": {
        "Region": {"type": "string", "description": "the region to query for this AMI"},
        "Filters": {"type": "object"},
        "Owners": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "ImageIds": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "ExecutableUsers": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string"},
        },
    },
}


class AMIProvider(ResourceProvider):
    def __init__(self):
        super(AMIProvider, self).__init__()

    @property
    def ec2(self):
        if self.get("Region") is not None:
            return boto3.client("ec2", region_name=self.get("Region"))
        return boto3.client("ec2")

    def create_describe_image_request(self):
        filters = []
        for k, v in self.get("Filters").items():
            filters.append({"Name": k, "Values": v if isinstance(v, list) else [v]})
        result = {
            n: (self.get(n) if isinstance(self.get(n), list) else [self.get(n)])
            for n in filter(
                lambda n: self.get(n) is not None,
                ["Owners", "ImageIds", "ExecutableUsers"],
            )
        }
        result["Filters"] = filters
        return result

    def get_image_id(self):
        request = self.create_describe_image_request()
        response = self.ec2.describe_images(**request)
        if len(response["Images"]) == 1:
            image = response["Images"][0]
            if image.get("State") == "available":
                self.physical_resource_id = image["ImageId"]
                self.set_attribute("KmsKeyIds", self.get_snapshot_kms_key_ids(image))
            else:
                self.fail(f"image {self.physical_resource_id} is not available (state = {image['State']}")
        else:
            self.fail("expected a single AMI, found {}".format(len(response["Images"])))
            self.physical_resource_id = "not-a-specific-ami"

    def get_snapshot_kms_key_ids(self, image: dict):
        kms_key_ids = []
        snapshot_ids = list(
            map(
                lambda m: m.get("Ebs").get("SnapshotId"),
                filter(
                    lambda m: m.get("Ebs") and "SnapshotId" in m.get("Ebs"),
                    image.get("BlockDeviceMappings", []),
                ),
            )
        )
        if snapshot_ids:
            paginator = self.ec2.get_paginator("describe_snapshots")
            for response in paginator.paginate(SnapshotIds=snapshot_ids):
                kms_key_ids.extend(
                    iter(
                        filter(
                            None, map(lambda s: s.get("KmsKeyId"), response["Snapshots"])
                        )
                    )
                )
        return kms_key_ids

    def create(self):
        self.get_image_id()

    def update(self):
        self.get_image_id()

    def delete(self):
        pass


provider = AMIProvider()


def handler(request, context):
    return provider.handle(request, context)
