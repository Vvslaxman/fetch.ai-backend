import json
import time
import logging
import requests
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Set up logging


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

# Server endpoint to send logs and execution times
server_endpoint = "http://127.0.0.1:5000/agent_output"

@supplier.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Supplier agent has started up.")
    ctx.logger.info(f"My address is {ctx.agent.address}")
    start_time = time.time() 

    # Fetch the job requirement from the Flask server
    response = requests.post('http://127.0.0.1:5000/submit_job', json={"item": "Chairs", "quantity": 30})
    job_data = response.json()
    output_log=[]
    if response.status_code == 200:
        item = job_data.get('item')
        quantity = job_data.get('quantity')
        if item is None or quantity is None:
            ctx.logger.error("Received data is missing 'item' or 'quantity'")
            return
        
        job = JobRequirements(item=item, quantity=quantity)
        output_log.append(f"Job requirement: {job.item} x {job.quantity}")
        
        # Process the job requirements as before
        with open("suppliers.json") as f:
            suppliers = json.load(f)
        
        filtered_suppliers = sorted(
            [s for s in suppliers if s['inventory'].get(job.item, 0) >= job.quantity],
            key=lambda x: x['review_score'],
            reverse=True
        )[:3]

        output_log.append(f"Top 3 suppliers: {filtered_suppliers}")

        supplier_selection = SupplierSelection(suppliers=filtered_suppliers)
        await ctx.send(quality_checker_address, supplier_selection)
        
        end_time = time.time()  # End timing
        execution_time = end_time - start_time  # Calculate elapsed time
        output_log.append(f"SupplierAgent execution time: {execution_time:.2f} seconds")

        
        # Send output data to the server
        output_data = {
            "agent_name": "SupplierAgent",
            "logs": "\n".join(output_log),
            "execution_time": execution_time,
            "top_suppliers": filtered_suppliers
        }
        requests.post(server_endpoint, json=output_data)

    else:
        ctx.logger.error("Failed to fetch job requirements from the server")

if __name__ == "__main__":
    supplier.run()
