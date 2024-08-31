from uagents import Agent, Context, Model
import time
import requests
import logging
from uagents.setup import fund_agent_if_low


class ImplementationConfirmation(Model):
    status: str

class BusinessConfirmation(Model):
    status: str

business_user = Agent(
    name="BusinessUserAgent",
    port=8006,
    seed="business_user secret phrase",
    endpoint=["http://127.0.0.1:8006/submit"]
)

fund_agent_if_low(business_user.wallet.address())

# Server endpoint to send logs and execution times
server_endpoint = "http://127.0.0.1:5000/agent_output"

@business_user.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Business User agent has started up.")
    ctx.logger.info(f"My address is {ctx.agent.address}")

@business_user.on_message(model=ImplementationConfirmation)
async def handle_implementation_confirmation(ctx: Context, sender: str, confirmation: ImplementationConfirmation):
    start_time = time.time()
    output_log=[]
    output_log.append(f"Received implementation confirmation: {confirmation.status}")

    business_confirmation = BusinessConfirmation(status="Confirmation Received")
    # Optionally, send this confirmation to a UI or other system if needed
    
    end_time = time.time()
    execution_time = end_time - start_time
    output_log.append(f"BusinessUserAgent execution time: {execution_time:.2f} seconds")
    # Send output data to the server
    output_data = {
        "agent_name": "BusinessUserAgent",
        "logs": "\n".join(output_log),
        "execution_time": execution_time,
        "status": business_confirmation.status
    }
    requests.post(server_endpoint, json=output_data)

if __name__ == "__main__":
    business_user.run()
