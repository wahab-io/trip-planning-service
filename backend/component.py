from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_ecs_patterns as ecs_patterns,
    aws_ecs as ecs,
)
from constructs import Construct


class Backend(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, cluster: ecs.Cluster, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table for trip plans
        self.trip_table = dynamodb.Table(
            self,
            "TripTable",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        # Flight MCP server
        flight_mcp_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            "FlightMCPService",
            cluster=cluster,
            cpu=1024,
            memory_limit_mib=2048,
            desired_count=1,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64
            ),
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("./flights-mcp"),
                container_port=6000,
            ),
        )

        # Backend API service
        self.backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "BackendService",
            cluster=cluster,
            cpu=2048,
            memory_limit_mib=4096,
            desired_count=1,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64
            ),
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("./backend"),
                container_port=80,
                environment={
                    "DYNAMODB_TABLE_NAME": self.trip_table.table_name,
                    "MCP_ENDPOINT": flight_mcp_service.load_balancer.load_balancer_dns_name
                    + ":6000",
                },
            ),
        )

        # Grant DynamoDB permissions to backend
        self.trip_table.grant_read_write_data(
            self.backend_service.task_definition.task_role
        )
