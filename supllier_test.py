from uagents import Agent, Context, Model

# Models for messaging
class SupplierRequest(Model):
    job_requirements: dict

class SupplierResponse(Model):
    suppliers: list

# Initialize the supplier agent with port 8000
supplier_agent = Agent(name="supplier_agent", port=8000,seed="supplier_secret_seed", endpoint="http://127.0.0.1:8000/submit")

@supplier_agent.on_event("startup")
async def startup(ctx: Context):
     ctx.logger.info(ctx.address)

@supplier_agent.on_message(model=SupplierRequest)
async def handle_supplier_request(ctx: Context, sender: str, msg: SupplierRequest):
    
    classified_suppliers = classify_suppliers(msg.job_requirements)
    if not classified_suppliers:
        ctx.logger.info("No suppliers meet the job requirements.")
        await ctx.send(sender, SupplierResponse(suppliers=[]))
        return

    ctx.logger.info(f"Classified Suppliers: {classified_suppliers}")

    if quality_check(classified_suppliers):
        ctx.logger.info("Quality check passed.")
        await ctx.send(sender, SupplierResponse(suppliers=classified_suppliers))
    else:
        ctx.logger.info("Quality check failed.")
        await ctx.send(sender, SupplierResponse(suppliers=[]))

def classify_suppliers(job_requirements):
    # Sample suppliers data
    suppliers = [
        {"id": 1, "name": "Supplier A", "price": 100, "quality_score": 90, "delivery_time": 5},
        {"id": 2, "name": "Supplier B", "price": 150, "quality_score": 85, "delivery_time": 3},
        {"id": 3, "name": "Supplier C", "price": 90, "quality_score": 80, "delivery_time": 7},
        {"id": 4, "name": "Supplier D", "price": 120, "quality_score": 88, "delivery_time": 4},
    ]

    classified_suppliers = []
    for supplier in suppliers:
        if (supplier['price'] <= job_requirements['max_price'] and
            supplier['quality_score'] >= job_requirements['min_quality_score'] and
            supplier['delivery_time'] <= job_requirements['max_delivery_time']):
            classified_suppliers.append(supplier)
    return classified_suppliers

def quality_check(classified_suppliers):
    import random
    return random.choices([True, False], weights=[90, 10], k=1)[0]

# Run the supplier agent
if __name__ == "__main__":
    supplier_agent.run()