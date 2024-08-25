from uagents import Agent, Context, Model

# Define the message models
class SupplierRequest(Model):
    job_requirements: dict

class SupplierResponse(Model):
    suppliers: list

# Initialize the client agent with a different port (8001)
client_agent = Agent(name="client_agent",port=8001, seed="client_secret_seed", endpoint="http://127.0.0.1:8001/submit")

@client_agent.on_interval(period=5.0)  # Automatically triggers every 5 seconds
async def request_suppliers(ctx: Context):
    """
    Sends a request to the supplier agent for classification and quality check.
    """
    supplier_agent_address = "agent1qwgnqmp5yezmusgd0r4twa5gzyrgl0dynv7q4qa93n94fvu2my0cq2j2dyn"  # The endpoint of the supplier agent

    job_requirements = {
        "max_price": 120,
        "min_quality_score": 85,
        "max_delivery_time": 5
    }
    
    req = SupplierRequest(job_requirements=job_requirements)
    ctx.logger.info("Sending supplier request...")
    
    try:
        await ctx.send(supplier_agent_address, req)
    except Exception as e:
        ctx.logger.error(f"Failed to send supplier request: {e}")

@client_agent.on_message(model=SupplierResponse)
async def handle_supplier_response(ctx: Context, sender: str, msg: SupplierResponse):
    """
    Handles the response from the supplier agent.
    """
    if not msg.suppliers:
        ctx.logger.info("No suppliers meet the job requirements or quality check failed.")
    else:
        ctx.logger.info(f"Suppliers that meet the criteria: {msg.suppliers}")

# Run the client agent
if __name__ == "__main__":
    client_agent.run()
