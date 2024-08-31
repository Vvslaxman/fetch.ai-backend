import json
import time
import logging
import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low


# Address of the Implementation agent
implementation_address = "agent1q2ukjfv5zsdnh79v7c8l6qw9g9xczxpfje75ucmmx8a7k800p735kf2u5wy"

class FinalSupplier(Model):
    supplier: dict

class TransportSelection(Model):
    transporter: dict

class TopTransporters(Model):
    top_transporters: list

transport_agent = Agent(
    name="TransportAgent",
    port=8004,
    seed="transport secret phrase",
    endpoint=["http://127.0.0.1:8004/submit"]
)

fund_agent_if_low(transport_agent.wallet.address())

# Server endpoint to send logs and execution times
server_endpoint = "http://127.0.0.1:5000/agent_output"

@transport_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Transport agent has started up.")
    ctx.logger.info(f"My address is {ctx.agent.address}")

@transport_agent.on_message(model=FinalSupplier)
async def handle_final_supplier(ctx: Context, sender: str, final_supplier: FinalSupplier):
    start_time = time.time() 
    output_log=[]
    ctx.logger.info(f"Received final supplier details: {final_supplier.supplier}")

    with open("transporters.json") as f:
        transporters = json.load(f)

    # Handle missing 'on_time_deliveries/total_deliveries' key
    valid_transporters = [
        t for t in transporters if 'on_time_deliveries/total_deliveries' in t
    ]

    if not valid_transporters:
        ctx.logger.error("No valid transporters with 'on_time_deliveries/total_deliveries' key found.")
        return

    # Show top 2 or 3 transporters
    top_transporters = sorted(
        valid_transporters,
        key=lambda x: x['on_time_deliveries/total_deliveries'],
        reverse=True
    )[:3]

    output_log.append(f"Top 2 or 3 transporters: {top_transporters}")

    # Select the final transporter from the top transporters
    final_transporter = top_transporters[0]  # Can use any filtering criteria

    output_log.append(f"Selected final transporter: {final_transporter}")

    # Send the top transporters to the quality checker agent for further analysis
    top_transporters_message = TopTransporters(top_transporters=top_transporters)
    await ctx.send(sender, top_transporters_message)

    # Send the final transporter to the implementation agent
    transport_selection = TransportSelection(transporter=final_transporter)
    await ctx.send(implementation_address, transport_selection)
    
    end_time = time.time()  # End timing
    execution_time = end_time - start_time  # Calculate elapsed time
    output_log.append(f"TransportAgent execution time: {execution_time:.2f} seconds")

    # Send output data to the server
    output_data = {
        "agent_name": "TransportAgent",
        "logs":"\n".join(output_log),
        "execution_time": execution_time,
        "selected_transporter": final_transporter,
        "top_transporters": top_transporters
    }
    requests.post(server_endpoint, json=output_data)

if __name__ == "__main__":
    transport_agent.run()
