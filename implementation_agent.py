from uagents import Agent, Context, Model
import time
import requests
import logging
from uagents.setup import fund_agent_if_low


# Address of the Business User agent
business_user_address = "agent1qwq8v4xp7uptzk5hzsyyv38jv65lhqkndjll0g3q4pyugl348g6q5rj0ajz"

class TransportSelection(Model):
    transporter: dict

class ImplementationConfirmation(Model):
    status: str

implementation = Agent(
    name="ImplementationAgent",
    port=8005,
    seed="implementation secret phrase",
    endpoint=["http://127.0.0.1:8005/submit"]
)

fund_agent_if_low(implementation.wallet.address())

# Server endpoint to send logs and execution times
server_endpoint = "http://127.0.0.1:5000/agent_output"

@implementation.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Implementation agent has started up.")
    ctx.logger.info(f"My address is {ctx.agent.address}")

@implementation.on_message(model=TransportSelection)
async def handle_transport_selection(ctx: Context, sender: str, transport_selection: TransportSelection):
    start_time = time.time()
    output_log=[]
    output_log.append(f"Received transport selection: {transport_selection.transporter}")

    # Process the transport selection and perform implementation
    implementation_confirmation = ImplementationConfirmation(status="Job Setup Completed")
    await ctx.send(business_user_address, implementation_confirmation)
    
    end_time = time.time()
    execution_time = end_time - start_time
    output_log.append(f"ImplementationAgent execution time: {execution_time:.2f} seconds")

    # Send output data to the server
    output_data = {
        "agent_name": "ImplementationAgent",
        "logs": "\n".join(output_log),
        "execution_time": execution_time,
        "status": implementation_confirmation.status
    }
    requests.post(server_endpoint, json=output_data)

if __name__ == "__main__":
    implementation.run()
