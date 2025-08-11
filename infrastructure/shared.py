from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from constructs import Construct

class Shared(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(self, "VPC", max_azs=2)
        self.cluster = ecs.Cluster(self, "Cluster", vpc=self.vpc)