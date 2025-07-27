# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import uuid
import os

from aws_lambda_powertools.event_handler.api_gateway import (
    APIGatewayRestResolver,
    CORSConfig,
)
from aws_lambda_powertools.event_handler.exceptions import InternalServerError
from aws_lambda_powertools.utilities.typing import LambdaContext

import boto3
from botocore.exceptions import ClientError

cors_config = CORSConfig(allow_origin="*")
app = APIGatewayRestResolver(cors=cors_config)

dynamodb = boto3.resource("dynamodb")

@app.post("/trip")
def trip():
    table_name = os.environ.get("TABLE_NAME")
    unique_id = uuid.uuid4()
        
    try:       
        trip_details = app.current_event.json_body
        table = dynamodb.Table(table_name) # type: ignore
        _ = table.put_item(
            Item={                
                "id": str(unique_id),
            },
        )
    except ClientError as error:
        raise InternalServerError(f"Internal Server Error: {error.response}") from error

    return {"id": str(unique_id)}, 201


@app.get("/history/<id>")
def history_detail(id: str):
    table_name = os.environ.get("TABLE_NAME")
    try:
        table = dynamodb.Table(table_name) # type: ignore
        response = table.get_item(Key={"id": id})
        print(response["Item"])
        return response["Item"]
    except ClientError as error:
        print(f"Unexpected error: {error}")
        raise InternalServerError(f"Internal Server Error: {error.response['Error']}") from error


def handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)