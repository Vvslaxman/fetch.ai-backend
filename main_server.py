from flask import Flask, render_template, jsonify
import requests
import threading

app = Flask(__name__)

# Endpoint to trigger all agents
@app.route('/run_all_agents', methods=['GET'])
def run_all_agents():
    outputs = {}

    def run_agent(agent_name, agent_port):
        try:
            response = requests.get(f'http://127.0.0.1:{agent_port}/run')
            outputs[agent_name] = response.text
        except requests.exceptions.RequestException as e:
            outputs[agent_name] = f"Error: {str(e)}"

    agent_ports = {
        "Supplier Agent": 8001,
        "Quality Checker Agent": 8003,
        "Transport Agent": 8004,
        "Implementation Agent": 8005,
        "Business User Agent": 8006
    }

    threads = []
    for agent_name, agent_port in agent_ports.items():
        thread = threading.Thread(target=run_agent, args=(agent_name, agent_port))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    return jsonify(outputs)

# Route to display the HTML page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
