import os
import logging
import boto3
from cfn_resource_provider import ResourceProvider

logging.basicConfig(level=os.getenv('LOG_LEVEL', 'INFO'))
log = logging.getLogger()

request_schema = {
    "type": "object",
    "required": ["Filters"],
    "properties": {
        "Region": {
            "type": "string",
            "description": "the region to query for this AMI"
        },
        "Filters": {
            "type": "object"
        },
        "Owners": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string"
            }
        },
        "ImageIds": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string"
            }
        },
        "ExecutableUsers": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string"
            }
        }
    }
}


class AMIProvider(ResourceProvider):

    def __init__(self):
        super(AMIProvider, self).__init__()

    @property
    def ec2(self):
        if self.get('Region') is not None:
            return boto3.client('ec2', region_name=self.get('Region'))
        return boto3.client('ec2')

    def create_describe_image_request(self):
        filters = []
        for k,v in self.get('Filters').items():
            filters.append({'Name': k, 'Values': v if isinstance(v, list) else [v]})
        result = {n: (self.get(n) if isinstance(self.get(n), list) else [self.get(n)])
                  for n in filter(lambda n : self.get(n) is not None, ['Owners', 'ImageIds', 'ExecutableUsers'])}
        result['Filters'] = filters
        return result

    def get_image_id(self):
        response = self.ec2.describe_images(**self.create_describe_image_request())
        if len(response['Images']) == 1:
            self.physical_resource_id = response['Images'][0]['ImageId']
        else:
            self.fail('expected a single AMI, found {}'.format(len(response['Images'])))
            self.physical_resource_id = 'not-a-specific-ami'

    def create(self):
        self.get_image_id()

    def update(self):
        self.get_image_id()

    def delete(self):
        pass


provider = AMIProvider()


def handler(request, context):
    return provider.handle(request, context)
