import json
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

class JobRequirements(Model):
    item: str
    quantity: int

class SupplierSelection(Model):
    suppliers: list

supplier = Agent(
    name="SupplierAgent",
    port=8001,
    seed="supplier secret phrase"
)

fund_agent_if_low(supplier.wallet.address())
quality_checker_address = "agent1qtl4zy63wgkps0wwruew5tfx2pn3z647vtm2acupgluvrqqmwcf8c4k3p03"
#keerdep
@supplier.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Supplier agent has started up.")
    ctx.logger.info(f"My address is {ctx.agent.address}")

    # Static job requirement (replace with one of your job examples)
    static_job = JobRequirements(item="Laptops", quantity=50)
    ctx.logger.info(f"Static job requirement: {static_job.item} x {static_job.quantity}")

    # Process the job requirement as if it were received via a message
    with open("suppliers.json") as f:
        suppliers = json.load(f)
    
    filtered_suppliers = sorted(
        [s for s in suppliers if s['inventory'].get(static_job.item, 0) >= static_job.quantity],
        key=lambda x: x['review_score'],
        reverse=True
    )[:3]

    ctx.logger.info(f"Top 3 suppliers: {filtered_suppliers}")

    supplier_selection = SupplierSelection(suppliers=filtered_suppliers)
    await ctx.send(quality_checker_address, supplier_selection)

if __name__ == "__main__":
    supplier.run()
