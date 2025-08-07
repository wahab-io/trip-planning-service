import datetime
import os
import re
from typing import Optional

import boto3
from pydantic import BaseModel, Field


class TripPlan(BaseModel):
    id: str
    origin: str = Field(default="San Francisco")
    from_date: datetime.date = Field(default=datetime.date.today())
    to_date: datetime.date = Field(
        default=datetime.date.today() + datetime.timedelta(days=7)
    )
    destination: str = Field(default="NYC")
    budget: int = Field(default=1000)


class TripPlanningService:
    def __init__(self) -> None:
        self.dynamodb = boto3.resource(
            "dynamodb",
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT", "http://localhost:8000"),
            region_name="us-east-1",
            aws_access_key_id="dummy",
            aws_secret_access_key="dummy",
        )  # type: ignore

    def add_trip(self, new_trip_plan: TripPlan) -> None:
        # Create table if it doesn't exist
        try:
            table = self.dynamodb.Table("trip-history")  # type: ignore
            table.load()
        except:
            table = self.dynamodb.create_table(  # pyright: ignore[reportAttributeAccessIssue]
                TableName="trip-history",
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            )
            table.wait_until_exists()

        item = new_trip_plan.model_dump()
        item["from_date"] = str(item["from_date"])
        item["to_date"] = str(item["to_date"])
        table.put_item(Item=item)  # type: ignore)

    def get_trip(self, _id: str):
        table = self.dynamodb.Table("trip-history")  # type: ignore
        result = table.get_item(Key={"id": _id})

        if not result.get("Item"):
            return None

        return result["Item"]

    def get_trip_recommendation(self, _id: str, recommendation_type) -> Optional[str]:
        table = self.dynamodb.Table("trip-history")  # type: ignore
        record = table.get_item(Key={"id": _id})

        if not record["Item"][recommendation_type]:
            return None

        return record["Item"][recommendation_type]

    def set_trip_recommendation(
        self, _id: str, recommendation_type: str, recommendation: str
    ) -> None:
        table = self.dynamodb.Table("trip-history")  # type: ignore
        record = table.get_item(Key={"id": _id})

        if not record.get("Item"):
            return

        table.update_item(
            Key={"id": _id},
            UpdateExpression=f"SET {recommendation_type} = :val",
            ExpressionAttributeValues={":val": recommendation},
        )
