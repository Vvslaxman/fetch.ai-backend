from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Define a message model for an order
class Order(Model):
    item: str
    quantity: int

# Define a message model for a confirmation
class Confirmation(Model):
    status: str

# Create the Transport agent with specific port and endpoint
transport = Agent(
    name="Transport",
    port=8002,
    seed="transport secret phrase",
    endpoint=["http://127.0.0.1:8002/submit"]
)

fund_agent_if_low(transport.wallet.address())

# Transport agent startup event
@transport.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Transport agent has started up.")
    ctx.logger.info(f"my adress:{ctx.address}")

# Transport receives the order and sends a confirmation
@transport.on_message(model=Order)
async def handle_order(ctx: Context, sender: str, order: Order):
    try:
        ctx.logger.info(f"Transport received order from {sender}: {order.item} x {order.quantity}")
        #ctx.logger.info(f"my adress:{ctx.address}")
        # Send a confirmation back to the supplier
        confirmation = Confirmation(status="Order Received")
        await ctx.send(sender, confirmation)  # Send back to the sender's address
    except Exception as e:
        ctx.logger.error(f"Error handling order: {e}")

# Periodically check for any specific tasks (if required)

# Run the Transport agent
if __name__ == "__main__":
    transport.run()
