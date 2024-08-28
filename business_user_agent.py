from uagents import Agent, Context, Model
import time
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

@business_user.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Business User agent has started up.")
    ctx.logger.info(ctx.agent.address)
     # Start timing

@business_user.on_message(model=ImplementationConfirmation)
async def handle_implementation_confirmation(ctx: Context, sender: str, confirmation: ImplementationConfirmation):
    start_time = time.time() 
    ctx.logger.info(f"Received implementation confirmation: {confirmation.status}")

    business_confirmation = BusinessConfirmation(status="Confirmation Received")
    # Optionally, send this confirmation to a UI or other system if needed
    end_time = time.time()  # End timing
    execution_time = end_time - start_time  # Calculate elapsed time
    ctx.logger.info(f"BusinessUserAgent execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    business_user.run()
