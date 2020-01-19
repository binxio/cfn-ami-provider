# Custom::AMI
The `Custom::AMI` resource is a lookup resource which returns the AMI id. 

## Syntax
To obtain the AMI id in your AWS CloudFormation template, use the following syntax:

```yaml
  Type : "Custom::AMI",
  Properties:
    Filters:
      '<filter-key>': '<filter-value> | [ <filter-value> ... ]'
      '<filter-key>': '<filter-value> | [ <filter-value> ... ]'
    Owners:
      - <owner>
      - <owner>
    ExecutableUsers: 
      - <user>
      - <user>
    ImageIds: 
      - <id>
      - <id>
    EnsureNumberOfKmsKeys: <integer>
    ServiceToken: String
```

After creation, the AMI id is returned.

## Properties
You can specify the following properties:

- `Filters`  - specifying the AMI you want the id of. See describe-images [--filters](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-images.html). required.
- `Owners`  - Filters the images by the owner (optional).
- `ImageIds`  - Scopes the selection to one or more image IDs (optional).
- `ExecutableUsers`  - Scopes the images by users with explicit launch permissions (optional).
- `ServiceToken`  - ARN pointing to the lambda function implementing this resource
- `ExpectedNumberOfKmsKeys` - The number of KMS keys that you expect to  be associated with the AMI.  


The custom resource wraps the EC2 [describe-images](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-images.html) function.

Note that the Filters argument has been turned into an object, to avoid the tedious repetition. Instead of:

```yaml
Filters:
 - Name: name
   Values: 
     - amzn-ami-2017.09.k-amazon-ecs-optimized 
 - Name: architecture
   Values: 
     - x86_64
```

you can simply write:

```yaml
Filters:
  name: amzn-ami-2017.09.k-amazon-ecs-optimized
  architecture: x86_64
```

If `ExpectedNumberOfKmsKeys` is specified than the resource will check that this number is actually in use. 
Normally just one KMS key is used per image, but it is possible to  have multiple snapshots each encrypted
with their own KMS key. To create KMS grants for the AMIs using the [KMS grant](https://github.com/binxio/cfn-kms-provider)
you can use this property to ensure you have made all the KMS grants required.




## Return values
With 'Fn::GetAtt' the following values are available:

- `KmsKeyIds` - array of length `ExpectedNumberOfKmsKeys` with KMS key ids associated with machine image
- `KmsKeyId` - the first KMS key id, if  `KmsKeyIds` has at least one.


