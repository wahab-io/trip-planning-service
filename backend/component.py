# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import typing
import builtins

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_cloudfront as cloudfront
from aws_cdk import aws_cloudfront_origins as origins
from aws_cdk import aws_s3_notifications as s3_notifications
from aws_cdk import aws_ssm as ssm


from backend.api import API


class Backend(cdk.Stack):
    def __init__(
        self,
        scope: typing.Optional[Construct] = None,
        _id: typing.Optional[builtins.str] = None,
    ) -> None:
        super().__init__(scope, _id)

        backend_api = API(self, "backend-api", self.region)

        ssm.StringParameter(
            self,
            "backend-api-endpoint",
            string_value=backend_api.apigw.url,
            parameter_name="backend-api-endpoint",
        )