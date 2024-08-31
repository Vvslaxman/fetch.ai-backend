document.addEventListener('DOMContentLoaded', () => {
    const runButton = document.getElementById('run');
    const agentSelect = document.getElementById('agent');
    const resultContent = document.getElementById('result-content');

    runButton.addEventListener('click', async () => {
        const agentName = agentSelect.value;
        try {
            const response = await fetch('http://127.0.0.1:5000/run_agent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ agent: agentName })
            });
            const data = await response.json();
            resultContent.textContent = `Result: ${JSON.stringify(data.result, null, 2)}\nExecution Time: ${data.execution_time} seconds`;
        } catch (error) {
            resultContent.textContent = `Error: ${error.message}`;
        }
    });
});
