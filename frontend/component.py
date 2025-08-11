from aws_cdk import (
    Stack, 
    aws_ecs_patterns as ecs_patterns, 
    aws_ecs as ecs
)
from constructs import Construct

class Frontend(Stack):
    def __init__(self, scope: Construct, construct_id: str, cluster: ecs.Cluster, backend_service: ecs_patterns.ApplicationLoadBalancedFargateService, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECS Fargate service to run Next.js frontend
        ecs_patterns.ApplicationLoadBalancedFargateService(self, "NextJSService",
            cluster=cluster,
            cpu=1024,
            memory_limit_mib=2048,
            desired_count=1,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64
            ),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("./frontend"),
                container_port=3000,
                environment={
                    "NEXT_PUBLIC_API_URL": f"http://{backend_service.load_balancer.load_balancer_dns_name}"
                }
            )
        )