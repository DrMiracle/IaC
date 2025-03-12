import pulumi
import pulumi_aws as aws
from variables import SSH_KEYS, AWS_REGION, SIZE, AMI, INSTANCES_NAMES

user_data = f"""#!/bin/bash
echo "{SSH_KEYS[1]}" >> /home/ubuntu/.ssh/authorized_keys
"""

# Key pair for connecting to AWS
key_pair = aws.ec2.KeyPair("my-keypair", public_key=SSH_KEYS[0])
aws_provider = aws.Provider("aws-provider", region=AWS_REGION)

security_group = aws.ec2.SecurityGroup('webserver-secgrp',
    description='Enable SSH access',
    # Incoming connections
    ingress=[
        { 'protocol': 'tcp',
          'from_port': 22,
          'to_port': 22,
          'cidr_blocks': ['0.0.0.0/0'] } # Allow SSH from anywhere
    ],
    # Outbound connections
    egress=[
        {"protocol": "-1",
         "from_port": 0,
         "to_port": 0,
         "cidr_blocks": ["0.0.0.0/0"]}, # No restrictions
    ])

# Creating multiple EC2 instances
instances = []
for name in INSTANCES_NAMES:
    instance = aws.ec2.Instance(name,
        instance_type=SIZE,
        ami=AMI,
        key_name=key_pair.key_name,
        user_data=user_data,
        vpc_security_group_ids=[security_group.id],
        tags={"Name": name},
        opts=pulumi.ResourceOptions(provider=aws_provider)
    )
    instances.append(instance)

# Restrict access to ports 5432-5435 only from these instances
for instance in instances:
    instance.tags["Name"].apply(lambda naming: aws.ec2.SecurityGroupRule(
        f"db-access-{naming}",
        type="ingress",
        from_port=5432,
        to_port=5435,
        protocol="tcp",
        security_group_id=security_group.id,
        source_security_group_id=security_group.id  # Allow only between these instances
    ))

# Export public and private IPs of instances
for instance in instances:
    pulumi.export(f"{INSTANCES_NAMES}_public_ip", instance.public_ip)
    pulumi.export(f"{INSTANCES_NAMES}_private_ip", instance.private_ip)