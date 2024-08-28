import json
import time
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Address of the Transport agent
transport_address = "agent1qty0qn043dpp7vfdyc27lppkarpn87xnz55crkej7kvnu503663yzw4wz5v"

class SupplierSelection(Model):
    suppliers: list

class FinalSupplier(Model):
    supplier: dict

class TopTransporters(Model):
    top_transporters: list

class TransportSelection(Model):
    transporter: dict

quality_checker = Agent(
    name="QualityCheckerAgent",
    port=8003,
    seed="quality_checker secret phrase",
    endpoint=["http://127.0.0.1:8003/submit"]
)

fund_agent_if_low(quality_checker.wallet.address())

@quality_checker.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Quality Checker agent has started up.")
    ctx.logger.info(ctx.address)

@quality_checker.on_message(model=SupplierSelection)
async def handle_supplier_selection(ctx: Context, sender: str, selection: SupplierSelection):
    start_time = time.time() 
    ctx.logger.info(f"Received supplier selection: {selection.suppliers}")

    with open("quality_check.json") as f:
        qc_criteria = json.load(f)

    final_supplier = min(
        selection.suppliers,
        key=lambda x: (
            x['review_score'],
            x['inventory'].get("Laptops", 0),
            x['inventory'].get("Chairs", 0)
        )
    )

    ctx.logger.info(f"Selected final supplier: {final_supplier}")

    final_supplier_message = FinalSupplier(supplier=final_supplier)
    await ctx.send(transport_address, final_supplier_message)
    end_time = time.time()  # End timing
    execution_time = end_time - start_time  # Calculate elapsed time
    ctx.logger.info(f"TransportAgent execution time: {execution_time:.2f} seconds")

@quality_checker.on_message(model=TopTransporters)
async def handle_top_transporters(ctx: Context, sender: str, top_transporters: TopTransporters):
    start_time=time.time()
    ctx.logger.info(f"Received top transporters: {top_transporters.top_transporters}")

    # Logic to select the best transporter based on QC criteria
    best_transporter = max(
        top_transporters.top_transporters,
        key=lambda x: x['on_time_deliveries/total_deliveries']
    )

    ctx.logger.info(f"Best transporter selected: {best_transporter}")

    transport_selection = TransportSelection(transporter=best_transporter)
    await ctx.send(transport_address, transport_selection)
    end_time = time.time()  # End timing
    execution_time = end_time - start_time  # Calculate elapsed time
    ctx.logger.info(f"TransportAgent execution time: {execution_time:.2f} seconds")

if __name__ == "__main__":
    quality_checker.run()
