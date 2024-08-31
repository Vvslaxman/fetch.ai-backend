from flask import Flask, jsonify, request
import subprocess
import time
import logging
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variable to store agent outputs
agent_outputs = {}

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MainServer")

@app.route('/submit_job', methods=['POST'])
def submit_job():
    data = request.json
    logger.info(f"Received job submission: {data}")
    return jsonify({"item": data.get("item"), "quantity": data.get("quantity")})

@app.route('/run_agents', methods=['POST'])
def run_agents():
    try:
        # Start each agent in a subprocess
        start_time = time.time()

        subprocess.Popen(['python3', 'D://unholy//agent//supplier_agent.py'])
        subprocess.Popen(['python3', 'D://unholy//agent//quality_checker_agent.py'])
        subprocess.Popen(['python3', 'D://unholy//agent//transport_agent.py'])
        subprocess.Popen(['python3', 'D://unholy//agent//implementation_agent.py'])
        subprocess.Popen(['python3', 'D://unholy//agent//business_user_agent.py'])

        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"All agents started in {execution_time:.2f} seconds")

        return jsonify({"status": "Agents started", "execution_time": execution_time})
    except Exception as e:
        logger.error(f"Error starting agents: {e}")
        return jsonify({"status": "Failed to start agents", "error": str(e)}), 500

@app.route('/agent_output', methods=['POST'])
def receive_agent_output():
    data = request.json
    agent_name = data.get("agent_name")
    if agent_name:
        # Store agent output in the global dictionary
        agent_outputs[agent_name] = data
        
        # Log the received data
        log_file = f'{agent_name.lower()}_agent.log'
        try:
            with open(log_file, 'a') as f:
                f.write(f"Execution time: {data.get('execution_time', 'N/A')} seconds\n")
                f.write(f"Logs:\n{data.get('logs', '')}\n\n")
            logger.info(f"Logs from {agent_name} saved successfully")
        except Exception as e:
            logger.error(f"Error saving logs for {agent_name}: {e}")
            return jsonify({"status": "Failed to save logs", "error": str(e)}), 500
        
    return jsonify({"status": "received"}), 200

@app.route('/fetch_agent_output', methods=['GET'])
def fetch_agent_output():
    return jsonify(agent_outputs), 200

@app.route('/fetch_logs', methods=['GET'])
def fetch_logs():
    log_files = ['supplier_agent.log', 'quality_checker_agent.log', 'transport_agent.log', 'implementation_agent.log', 'business_user_agent.log']
    logs = {}
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                logs[log_file.replace('.log', '')] = f.read()
        except FileNotFoundError:
            logs[log_file.replace('.log', '')] = 'Log file not found.'
    
    return jsonify(logs)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
