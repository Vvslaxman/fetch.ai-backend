from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/submit_job', methods=['POST'])
def submit_job():
    data = request.json
    item = data.get("item")
    quantity = data.get("quantity")
    
    # Validate the input
    if not item or not quantity:
        return jsonify({"error": "Invalid input"}), 400
    
    # Return the same data structure that supplier_agent.py expects
    return jsonify({"item": item, "quantity": quantity}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
