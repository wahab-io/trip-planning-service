from constructs import Construct
from aws_cdk import (
    CustomResource,
    aws_lambda as _lambda,
    aws_iam as iam,
    custom_resources as cr,
    Duration
)

class Agent(Construct):
    def __init__(self, scope: Construct, id: str, agent_name: str, **kwargs):
        super().__init__(scope, id)
        
        
