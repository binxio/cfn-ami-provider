# cfn-ami-provider
A CloudFormation custom resource provider for declaring AMIs by name.

When you want to start a virtual machine using CloudFormation, you always have to specify 
an Amazon Machine Image (AMI) id like `ami-1fefd19`.  hese ids are difficult to find, give you 
no idea on what kind of image its and are different per region. 

With this custom CloudFormation Provider you get rid of the magic strings and specify AMIs by name, 
which will ease the understandibility and maintainability of your CloudFormation templates.


## How do get the AMI id by name?
It is quite easy: you specify a CloudFormation resource of the [Custom::AMI](docs/Custom%3A%3AMI.md), as follows:

```yaml
  AMI:
    Type: Custom::AMI
    Properties:
      Filters:
        name: 'amzn-ami-2017.09.a-amazon-ecs-optimized'
      ServiceToken: !Sub 'arn:aws:lambda:${AWS::Region}:${AWS::AccountId}:function:binxio-cfn-ami-provider'
      
  Instance:
    Type: AWS:EC2::Instance
    EC2Instance:
        Type: AWS::EC2::Instance
        Properties:
            ImageId: !Ref AMI
```

This is the most simple use case. If you want, you can go wild and specify any of the parameters of the EC2 [describe-images](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-images.html) API call.

## Keeping your AMI up to date
Every now and then a new version of your AMI will be released. You can keep the AMIs up to date by using
the [aws-cfn-update](https://github.com/binxio/aws-cfn-update) utility:

```
aws-cfn-update latest-ami --ami-name-pattern 'amzn-ami-2017.09.a-amazon-ecs-optimized' .
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

This CloudFormation template will use our pre-packaged provider from `s3://binxio-public-${AWS_REGION}/lambdas/cfn-ami-provider-0.1.4.zip`.


## Demo
To install the simple sample of the Custom Resource, type:

```sh
aws cloudformation create-stack --stack-name cfn-ami-provider-demo \
	--template-body file://cloudformation/demo-stack.json
aws cloudformation wait stack-create-complete  --stack-name cfn-ami-provider-demo
```

## Conclusion
With this custom CloudFormation Provider you can declare an AMI by name, which will ease
the understandibility and maintainability of your CloudFormation templates.
