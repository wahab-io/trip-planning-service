import datetime
import os
from enum import Enum

from pydantic import BaseModel

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import boto3
from strands import Agent


class RecommendationType(str, Enum):
    LODGING = "lodging"
    FOOD = "food"
    TRAVEL = "travel"


class TripPlanRequest(BaseModel):
    id: str
    from_date: datetime.date
    to_date: datetime.date
    location: str
    budget: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/plan/{id}")
async def get_plan(id: str):
    # retrieve the request parameters from DynamoDB
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000"),
        region_name="us-east-1",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )
    table = dynamodb.Table("trip-history")  # type: ignore
    response = table.get_item(Key={"id": id})
    print("Retrieved request from DynamoDB")
    return response["Item"]


@app.post("/plan")
async def new_plan(request: TripPlanRequest):
    # store the request parameters in DynamoDB
    dynamodb = boto3.resource(
        "dynamodb",
        endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000"),
        region_name="us-east-1",
        aws_access_key_id="dummy",
        aws_secret_access_key="dummy",
    )

    # Create table if it doesn't exist
    try:
        table = dynamodb.Table("trip-history")  # type: ignore
        table.load()
    except:
        table = dynamodb.create_table( # type: ignore
            TableName="trip-history",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()

    item = request.model_dump()
    item["from_date"] = str(item["from_date"])
    item["to_date"] = str(item["to_date"])
    table.put_item(Item=item)
    print("Stored request in DynamoDB")
    return {"id": request.id}


@app.get("/plan/{id}/recommendation/{recommendation_type}")
async def get_plan_recommendation(id: str, recommendation_type: str):
    async def generate():
        # retrieve the plan values from DynamoDB
        dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000"),
            region_name="us-east-1",
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )
        table = dynamodb.Table("trip-history")  # type: ignore
        response = table.get_item(Key={"id": id})
        location = response["Item"]["location"]
        from_date = response["Item"]["from_date"]
        to_date = response["Item"]["to_date"]
        budget = response["Item"]["budget"]

        # This code checks if a recommendation of the specified type already exists in DynamoDB
        # If it exists, return the cached recommendation instead of generating a new one
        # response["Item"].get(recommendation_type) checks if the recommendation_type key exists
        # If found, yield the existing recommendation stored in DynamoDB
        if response["Item"].get(recommendation_type):
            yield response["Item"][recommendation_type]

        else:

            agent = Agent(
                model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
                tools=[],
                callback_handler=None,
            )

            prompt = f"""
            I am planning a trip to {location} from {from_date} to {to_date} with a budget of {budget} USD.
            Please provide brief {recommendation_type} recommendation during my travel.
            """

            full_response = ""
            try:
                async for event in agent.stream_async(prompt):
                    if "data" in event:
                        chunk = event["data"]
                        full_response += chunk
                        yield chunk

                # Store the complete response in DynamoDB
                table.update_item(
                    Key={"id": id},
                    UpdateExpression=f"SET {recommendation_type} = :response",
                    ExpressionAttributeValues={":response": full_response},
                )
                print("Stored response in DynamoDB")
            except Exception as e:
                yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")
