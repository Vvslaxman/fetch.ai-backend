import json
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Address of the Implementation agent
implementation_address = "agent1q2ukjfv5zsdnh79v7c8l6qw9g9xczxpfje75ucmmx8a7k800p735kf2u5wy"

class FinalSupplier(Model):
    supplier: dict

class TransportSelection(Model):
    transporter: dict

transport_agent = Agent(
    name="TransportAgent",
    port=8004,
    seed="transport secret phrase",
    endpoint=["http://127.0.0.1:8004/submit"]
)

fund_agent_if_low(transport_agent.wallet.address())

@transport_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Transport agent has started up.")
    ctx.logger.info(ctx.agent.address)

@transport_agent.on_message(model=FinalSupplier)
async def handle_final_supplier(ctx: Context, sender: str, final_supplier: FinalSupplier):
    ctx.logger.info(f"Received final supplier details: {final_supplier.supplier}")

    with open("transporters.json") as f:
        transporters = json.load(f)
    
    selected_transporter = min(
        transporters,
        key=lambda x: x['delivery_time_days']
    )
    
    ctx.logger.info(f"Selected transporter: {selected_transporter}")

    transport_selection = TransportSelection(transporter=selected_transporter)
    await ctx.send(implementation_address, transport_selection)

if __name__ == "__main__":
    transport_agent.run()
