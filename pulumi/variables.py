# public keys
SSH_KEYS = [
    open("ssh-keys/public_key.pub").read().strip(),
    open("ssh-keys/id_ed25519.pub").read().strip(),
]

# EC2
AWS_REGION = "eu-north-1"
SIZE = "t3.micro"
AMI = "ami-04542995864e26699"

# instances
INSTANCES_NAMES = ["server-1", "server-2"]