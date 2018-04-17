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
