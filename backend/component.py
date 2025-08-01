# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

from inspect import stack
import typing
import builtins

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import aws_ssm as ssm


class Backend(cdk.Stack):
    def __init__(
        self,
        scope: typing.Optional[Construct] = None,
        _id: typing.Optional[builtins.str] = None,
    ) -> None:
        super().__init__(scope, _id)

        stack_id_prefix = "backend"
        