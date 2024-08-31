import json
import time
import logging
import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Address of the Transport agent
transport_address = "agent1qty0qn043dpp7vfdyc27lppkarpn87xnz55crkej7kvnu503663yzw4wz5v"

# Server endpoint to send logs and execution times
server_endpoint = "http://127.0.0.1:5000/agent_output"

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
    ctx.logger.info(ctx.agent.address)

@quality_checker.on_message(model=SupplierSelection)
async def handle_supplier_selection(ctx: Context, sender: str, selection: SupplierSelection):
    start_time = time.time()
    output_log = []

    output_log.append(f"Received supplier selection: {selection.suppliers}")

    with open("quality_check.json") as f:
        qc_criteria = json.load(f)

    # Modify selection logic using QC criteria
    final_supplier = min(
        selection.suppliers,
        key=lambda x: (
            qc_criteria.get('review_score_weight', 1) * x['review_score'],
            qc_criteria.get('inventory_weight', 1) * x['inventory'].get("Laptops", 0),
            qc_criteria.get('inventory_weight', 1) * x['inventory'].get("Chairs", 0)
        )
    )
    output_log.append(f"Selected final supplier: {final_supplier}")

    final_supplier_message = FinalSupplier(supplier=final_supplier)
    await ctx.send(transport_address, final_supplier_message)

    end_time = time.time()
    execution_time = end_time - start_time
    output_log.append(f"TopSupplier execution time: {execution_time:.2f} seconds")

    # Send output data to the server
    output_data = {
        "agent_name": "QualityCheckerAgent",
        "logs": "\n".join(output_log),
        "execution_time": execution_time,
        "final_supplier": final_supplier
    }
    requests.post(server_endpoint, json=output_data)

@quality_checker.on_message(model=TopTransporters)
async def handle_top_transporters(ctx: Context, sender: str, top_transporters: TopTransporters):
    start_time = time.time()
    output_log1 = []

    output_log1.append(f"Received top transporters: {top_transporters.top_transporters}")

    with open("quality_check.json") as f:
        qc_criteria = json.load(f)

    # Modify transporter selection logic using QC criteria
    best_transporter = max(
        top_transporters.top_transporters,
        key=lambda x: (
            qc_criteria.get('delivery_weight', 1) * x['on_time_deliveries/total_deliveries']
        )
    )
    output_log1.append(f"Best transporter selected: {best_transporter}")

    transport_selection = TransportSelection(transporter=best_transporter)
    await ctx.send(transport_address, transport_selection)

    end_time = time.time()
    execution_time = end_time - start_time
    output_log1.append(f"TopTransporter execution time: {execution_time:.2f} seconds")

    # Send output data to the server
    output_data1 = {
        "agent_name": "QualityCheckerAgent",
        "logs": "\n".join(output_log1),
        "execution_time": execution_time,
        "best_transporter": best_transporter
    }
    requests.post(server_endpoint, json=output_data1)

if __name__ == "__main__":
    quality_checker.run()
