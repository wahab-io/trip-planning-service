import datetime
import os
from enum import Enum

from pydantic import BaseModel

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import boto3
from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

from dotenv import load_dotenv
from .service import TripPlanningService, TripPlan

load_dotenv()


class RecommendationType(str, Enum):
    LODGING = "lodging"
    FOOD = "food"
    TRAVEL = "travel"


class PlanHistory(BaseModel):
    id: str
    origin: str
    from_date: datetime.date
    to_date: datetime.date
    destination: str
    budget: int
    lodging: str
    food: str
    travel: str


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = TripPlanningService()


@app.get("/plan/{id}")
async def get_plan(id: str, response: Response):
    trip = service.get_trip(id)

    if not trip:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Trip not found"}

    return trip


@app.post("/plan")
async def new_plan(request: TripPlan):
    service.add_trip(request)
    return {"id": request.id}


@app.get("/plan/{id}/recommendation/lodging")
async def get_plan_lodging_recommendation(id: str):
    async def generate():
        # service = TripPlanningService()
        record = service.get_trip(id)
        if record.get(RecommendationType.LODGING):
            yield record[RecommendationType.LODGING]

        else:
            try:
                location = record["destination"]
                from_date = record["from_date"]
                to_date = record["to_date"]
                budget = record["budget"]
                agent = Agent(
                    model="us.deepseek.r1-v1:0",
                    system_prompt=f"""You are a lodging specialist helping find accommodations in {location}
                    from {from_date} to {to_date}. Provide hotel and accommodation recommendations.""",
                    callback_handler=None,
                )

                prompt = """
                Please provide brief lodging recommendation during my travel.            
                """

                reasoning = "<reasoning>"
                response = "<response>"

                async for event in agent.stream_async(prompt):
                    if "reasoningText" in event:
                        chunk = "<reasoning>" + event["reasoningText"] + "</reasoning>"
                        reasoning += event["reasoningText"]
                        yield chunk
                    if "data" in event:
                        chunk = "<response>" + event["data"] + "</response>"
                        response += event["data"]
                        yield chunk

                reasoning += "</reasoning>"
                response += "</response>"
                full_response = reasoning + response
                # Store the complete response in DynamoDB
                service.set_trip_recommendation(id, "lodging", full_response)
                # table.update_item(
                #     Key={"id": id},
                #     UpdateExpression="SET lodging = :response",
                #     ExpressionAttributeValues={":response": full_response},
                # )
                print("Stored lodging response in DynamoDB")
            except Exception as e:
                yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/plan/{id}/recommendation/food")
async def get_plan_food_recommendation(id: str):
    async def generate():
        # retrieve the plan values from DynamoDB
        record = service.get_trip(id)
        if record.get(RecommendationType.FOOD):
            yield record[RecommendationType.FOOD]

        else:
            destination = record["destination"]
            from_date = record["from_date"]
            to_date = record["to_date"]
            budget = record["budget"]
            agent = Agent(
                model="us.deepseek.r1-v1:0",
                system_prompt=f"""You are a food and dining specialist for {destination} 
                from {from_date} to {to_date} with a budget of ${budget}. 
                Recommend restaurants, local cuisine, and dining experiences.""",
                callback_handler=None,
            )

            prompt = """
            Please provide brief food recommendation during my travel.            
            """

            full_response = ""
            try:
                async for event in agent.stream_async(prompt):
                    if "data" in event:
                        chunk = event["data"]
                        full_response += chunk
                        yield chunk

                # Store the complete response in DynamoDB
                service.set_trip_recommendation(id, "food", full_response)
                print("Stored food response in DynamoDB")
            except Exception as e:
                yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/plan/{id}/recommendation/travel")
async def get_plan_travel_recommendation(id: str):
    async def generate():
        record = service.get_trip(id)
        if record.get(RecommendationType.TRAVEL):
            yield record[RecommendationType.TRAVEL]

        else:
            mcp_endpoint = os.getenv("MCP_ENDPOINT", "localhost:6000")
            flights_mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command="socat",
                        args=["-", f"TCP:{mcp_endpoint}"],
                    )
                )
            )

            with flights_mcp_client:
                origin = record["origin"]
                destination = record["destination"]
                from_date = record["from_date"]
                to_date = record["to_date"]
                budget = record["budget"]

                tools = flights_mcp_client.list_tools_sync()
                agent = Agent(
                    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                    tools=[tools],
                    callback_handler=None,
                    system_prompt=f"""You are a helpful travel agent helping search flights and local transportation information.
                    Provide flights recommendation from {origin} to {destination} for dates {from_date} to {to_date}.
                    The flights need to be within the budget of ${budget} USD. Only use half of the budget for flights and local transportation.
                    Use the flight search tools to find flights. Always use SFO as the origin airport code.""",
                )

                prompt = f"""
                Please provide brief travel recommendation during my travel.
                Output the response with "Here is your travel and transportation recommendation."
                
                Break down the recommendation in two sections:
                - ## Flights
                - ## Location Transportation

                For each section provide tips, that can be helpful and relevant to the {destination}.
                Maximum use 150 words to limit your response.
                """

                full_response = ""
                try:
                    async for event in agent.stream_async(prompt):
                        if "data" in event:
                            chunk = event["data"]
                            full_response += chunk
                            yield chunk

                    # Store the complete response in DynamoDB
                    service.set_trip_recommendation(id, "travel", full_response)
                    print("Stored travel response in DynamoDB")
                except Exception as e:
                    yield f"Error: {str(e)}"

    return StreamingResponse(generate(), media_type="text/plain")
