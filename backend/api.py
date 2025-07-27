# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from os import path

from constructs import Construct
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_logs as logs
import aws_cdk as cdk


class API(Construct):
    def __init__(
        self,
        scope: Construct,
        _id: str,
        region: str,
    ) -> None:
        super().__init__(scope, _id)

        if region is None:
            raise ValueError("Region is required")

        # create dynamodb table to store plan history
        self.history_table = dynamodb.Table(
            self,
            "history-table",
            partition_key=dynamodb.Attribute(
                name="id", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )
        
        python_version = "python313"
        layer_arn = f"arn:aws:lambda:{region}:017000801446:layer:AWSLambdaPowertoolsPythonV3-{python_version}-arm64:18"
        lambda_powertools_layer = lambda_.LayerVersion.from_layer_version_arn(
            self, "lambda-powertools-layer", layer_arn
        )


        self.trip_planning_function = lambda_.Function(
            self,
            "rest-backend-func",
            runtime=lambda_.Runtime.PYTHON_3_13,
            code=lambda_.Code.from_asset(
                path.join(path.dirname(__file__), "lambda")
            ),
            handler="index.handler",
            layers=[lambda_powertools_layer],
            environment={
                "TABLE_NAME": self.history_table.table_name
            },
        )

        rest_backend_func_role = self.trip_planning_function.role
        self.history_table.grant_read_write_data(rest_backend_func_role) # type: ignore

        access_logs = logs.LogGroup(
            self,
            "access-logs",
            log_group_name="rest-api-access-logs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        self.apigw = apigw.LambdaRestApi(
            self,
            "rest-api",
            handler=self.trip_planning_function, # type: ignore            
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
            ),
            cloud_watch_role=True,
            deploy_options=apigw.StageOptions(
                tracing_enabled=True,
                logging_level=apigw.MethodLoggingLevel.INFO,
                access_log_destination=apigw.LogGroupLogDestination(access_logs), # type: ignore
                access_log_format=apigw.AccessLogFormat.json_with_standard_fields(
                    caller=True,
                    http_method=True,
                    ip=True,
                    protocol=True,
                    request_time=True,
                    resource_path=True,
                    response_length=True,
                    status=True,
                    user=True,
                ),
            ),
        )