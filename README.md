# cfn-ami-provider
A CloudFormation custom resource provider for declaring AMIs by name

When you want to start a virtual machine using CloudFormation, you always have to specify 
an Amazon Machine Image (AMI) id. These ids are non-descriptive: you have no idea what kind of 
machine `ami-f15ff69e' is. More over, for the same machine has different ids in different regions making
it even more difficult to create a template which works in any region.

## How do get the AMI id by name?
It is quite easy: you specify a CloudFormation resource of the [Custom::AMI](docs/Custom%3A%3AMI.md), as follows:

```yaml
  AMI:
    Type: Custom::AMI
    Properties:
      Filters:
        name: 'amzn-ami-2017.09.k-amazon-ecs-optimized'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-ami-provider'
      
  Instance:
    Type: AWS:EC2::Instance
    EC2Instance:
        Type: AWS::EC2::Instance
        Properties:
            ImageId: !Ref AMI
```

## Installation
To install this custom resource, type:

```sh
aws cloudformation create-stack \
	--capabilities CAPABILITY_IAM \
	--stack-name cfn-ami-provider \
	--template-body file://cloudformation/cfn-ami-provider.json 

aws cloudformation wait stack-create-complete  --stack-name cfn-ami-provider 
```

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public-${AWS_REGION}/lambdas/cfn-ami-provider-0.11.0.zip`.


## Demo
To install the simple sample of the Custom Resource, type:

```sh
aws cloudformation create-stack --stack-name cfn-ami-provider-demo \
	--template-body file://cloudformation/demo-stack.json
aws cloudformation wait stack-create-complete  --stack-name cfn-ami-provider-demo
```

## Conclusion
With this custom AMI resource provider, the specification of AMI id is easier to maintain and read.
