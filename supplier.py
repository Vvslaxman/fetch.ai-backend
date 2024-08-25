from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low


transport_adress="agent1qty0qn043dpp7vfdyc27lppkarpn87xnz55crkej7kvnu503663yzw4wz5v"

# Define a message model for an order
class Order(Model):
    item: str
    quantity: int

# Define a message model for a confirmation
class Confirmation(Model):
    status: str

# Create the Supplier agent with specific port and endpoint
supplier = Agent(
    name="Supplier",
    port=8001,
    seed="supplier secret phrase",
    endpoint=["http://127.0.0.1:8001/submit"]
)

fund_agent_if_low(supplier.wallet.address())

# Supplier sends an order to the Transport on startup
@supplier.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Supplier agent has started up.")

# Supplier sends an order to the Transport at regular intervals
@supplier.on_interval(period=10)  # Send an order every 10 seconds
async def send_order(ctx: Context):
    try:
        order = Order(item="Widgets", quantity=100)
        ctx.logger.info(f"Supplier sending order: {order.item} x {order.quantity}")
        # Send directly to the Transport agent's address
        #ctx.logger.info(f'my adress:{ctx.address}')
        await ctx.send(transport_adress, order)
    except Exception as e:
        ctx.logger.error(f"Error sending order: {e}")

# Supplier receives the confirmation
@supplier.on_message(model=Confirmation)
async def handle_confirmation(ctx: Context, sender: str, confirmation: Confirmation):
    try:
        ctx.logger.info(f"Supplier received confirmation from {sender}: {confirmation.status}")
    except Exception as e:
        ctx.logger.error(f"Error handling confirmation: {e}")

# Run the Supplier agent
if __name__ == "__main__":
    supplier.run()
