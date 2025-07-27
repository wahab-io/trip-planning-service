from aws_cdk import (
    Stack, 
    aws_ecs_patterns as ecs_patterns, 
    aws_ecs as ecs
)
from constructs import Construct

class Frontend(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ecs fargate service to run next.js frontend
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "NextJSService",
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("./frontend"),
                container_port=3000
            )
        )        