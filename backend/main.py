import datetime
import os
from enum import Enum

from pydantic import BaseModel

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

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
                destination = record["destination"]
                from_date = record["from_date"]
                to_date = record["to_date"]
                budget = record["budget"]
                agent = Agent(
                    model="us.deepseek.r1-v1:0",
                    # DeepSeek R1 recommends not to use system prompt
                    # See https://docs.together.ai/docs/prompting-deepseek-r1
                    # system_prompt=f"""You are a helpful travel agent, who provides lodging recommendations.
                    # Provide hotel and accommodation recommendations.""",
                    callback_handler=None,
                )

                prompt = f"""
                Act as a travel advisor specializing in budget-conscious lodging recommendations. You are CONCISE in your response. The user has provided:

                1. {destination}
                2. Travel start {from_date} and end date {to_date} (to determine duration and season)
                3. Total trip budget {budget} (lodging should use ≤50% of this).
                
                Your task is to:

                Calculate the maximum lodging budget (50% of total) and per-night allowance (total lodging budget ÷ duration).
                Analyze weather patterns at the destination during the travel dates (e.g., rainy season, extreme temperatures, peak summer/winter). Highlight how this might impact lodging choices (e.g., need for AC, heating, or indoor amenities).
                Recommend 3-4 accommodation categories (e.g., boutique hotels, hostels, vacation rentals) suited to the budget, duration, and weather. Explain why each fits (e.g., 'Vacation rentals offer kitchens for longer stays' or 'Hostels save costs for solo travelers').
                Suggest specific features to prioritize (e.g., proximity to public transit if rainy, pools for summer, cozy common areas for winter).
                Provide a budget breakdown example (e.g., 'With a $2,000 total budget, allocate $1,000 for 7 nights = ~$143/night. Opt for mid-range hotels or private Airbnb rooms').
                
                Example response structure:

                Weather Insights: 'Expect warm, humid days (85°F) in Bali during July. Prioritize AC and pool access.'
                Budget Analysis: '$1,500 total budget → $750 for lodging. At 10 nights, aim for ≤$75/night.'
                Recommendations: '1. Guesthouses ($50–$70/night): Budget-friendly with AC. 2. Boutique hotels ($80–$100/night: Splurge for shorter stays). 3. Hostels ($20–$30/bed: Ideal for extending your trip).'
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
                # system_prompt=f"""You are a helpful food and dining specialist for {destination}
                # from {from_date} to {to_date} with a budget of ${budget}.
                # """,
                callback_handler=None,
            )

            prompt = f"""
            Act as a travel advisor specializing in food and dining recommendations. The user has provided:

            1. {destination}
            2. Travel dates {from_date} to {to_date}
            3. Total trip budget ${budget} (food should use ≤25% of this).

            Your task is to:

            1. Calculate the maximum food budget (25% of total).
            2. Recommend 3-4 food categories (e.g., fine dining, local cuisine, street food) suited to the budget and duration.
            3. Suggest specific features to prioritize (e.g., proximity to public transit, local cuisine, street food).
            4. Provide a budget breakdown example (e.g., 'With a $2, 000 total budget, allocate $500 for 7 days stay = ~$71/day. Provide breakdowns for lunch and dinner').

            Example response structure:

            Budget Analysis: '$1,500 total budget → $375 for food. At 10 nights, aim for ≤$37.5/day.'
            Recommendations: '1. Fine dining ($100–$200/meal): Budget-friendly with AC. 2. Local cuisine ($50–$70/meal: Splurge for shorter stays). 3. Street food ($20–$30/meal: Ideal for extending your trip).'
            """

            reasoning = "<reasoning>"

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
                    system_prompt="""You are a helpful travel agent helping search flights and 
                    local transportation information. Use the flight search tools to find flights. 
                    Always use SFO as the origin airport code.""",
                )

                prompt = f"""
                Provide flights recommendation from {origin} to {destination} for dates {from_date} to {to_date}.
                Only use 25% of ${budget} for flights and local transportation.
                Return the response in markdown format.
                Please provide brief travel recommendation during my travel.
                Output the response with: \n\n"Here is your travel and transportation recommendations."
                
                Break down the recommendation in two sections:
                - *Flights*
                - *Location Transportation*

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
