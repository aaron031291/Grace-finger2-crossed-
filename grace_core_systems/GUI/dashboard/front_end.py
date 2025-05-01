<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <title>Grace Cognitive Dashboard</title>
    <style>
        :root {
            --grace-blue: #4299e1;
            --grace-dark: #1a202c;
            --grace-light: #cbd5e0;
        }
        body { margin: 0; padding: 20px; }
        .hidden { display: none !important; }
        #cy { width: 100%; height: 70vh; border: 1px solid #4a5568; margin: 20px 0; }
        .grace-panel { background: #2d3748; color: var(--grace-light); padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .grace-btn { background: var(--grace-blue); color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .grace-btn:hover { opacity: 0.9; }
        .grid { display: grid; gap: 20px; }
        .grid-cols-2 { grid-template-columns: repeat(2, 1fr); }
    </style>
</head>
<body>
    <div id="login" class="grace-panel" style="max-width: 400px;">
        <h2 style="margin-top: 0;">Grace Authentication</h2>
        <div style="display: grid; gap: 10px;">
            <input type="text" id="username" placeholder="Username" style="padding: 8px; background: #2d3748; border: 1px solid #4a5568; color: var(--grace-light);">
            <input type="password" id="password" placeholder="Password" style="padding: 8px; background: #2d3748; border: 1px solid #4a5568; color: var(--grace-light);">
            <button onclick="login()" class="grace-btn">Authenticate</button>
        </div>
    </div>

    <div id="dashboard" class="hidden">
        <div class="grace-panel">
            <h2 style="margin-top: 0;">Live Cognitive Map</h2>
            <div id="cy"></div>
        </div>

        <div class="grid grid-cols-2">
            <div class="grace-panel">
                <h2 style="margin-top: 0;">System Health</h2>
                <pre id="healthData" style="white-space: pre-wrap;"></pre>
            </div>
            
            <div class="grace-panel">
                <h2 style="margin-top: 0;">Command Console</h2>
                <div style="display: grid; gap: 10px;">
                    <select id="commandSelect" style="padding: 8px; background: #2d3748; border: 1px solid #4a5568; color: var(--grace-light);">
                        <option value="trigger_audit">Trigger Audit</option>
                        <option value="force_rollback">Force Rollback</option>
                    </select>
                    <button onclick="executeCommand()" class="grace-btn">Execute</button>
                    <pre id="commandOutput" style="background: #1a202c; padding: 10px; border-radius: 4px; max-height: 200px; overflow: auto;"></pre>
                </div>
            </div>
        </div>
    </div>

    <script src="https://unpkg.com/cytoscape@3.23.0/dist/cytoscape.min.js"></script>
    <script>
        let authToken = null;
        let cy = null;
        const graceBlue = getComputedStyle(document.documentElement).getPropertyValue('--grace-blue');

        function initCy() {
            cy = cytoscape({
                container: document.getElementById('cy'),
                elements: [],
                style: [{
                    selector: 'node',
                    style: {
                        'label': 'data(id)',
                        'background-color': graceBlue,
                        'text-valign': 'center',
                        'width': 40,
                        'height': 40
                    }
                }, {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': graceBlue,
                        'curve-style': 'bezier'
                    }
                }]
            });
        }

        async function login() {
            try {
                const formData = new URLSearchParams({
                    username: document.getElementById('username').value,
                    password: document.getElementById('password').value,
                    grant_type: 'password'
                });

                const response = await fetch('/token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json'
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Login failed: ${response.status}`);
                }

                const data = await response.json();
                authToken = data.access_token;
                
                document.getElementById('login').classList.add('hidden');
                document.getElementById('dashboard').classList.remove('hidden');
                
                initCy();
                connectWebSocket();
                startHealthPolling();
            } catch (error) {
                alert(error.message);
                console.error('Login error:', error);
            }
        }

        function connectWebSocket() {
            const ws = new WebSocket(`ws://${window.location.host}/ws/cognitive-map?token=${authToken}`);
            
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                cy.add(data);
                cy.layout({ name: 'cose' }).run();
            };
        }

        async function startHealthPolling() {
            const updateHealth = async () => {
                try {
                    const response = await fetch('/module-health', {
                        headers: { 'Authorization': `Bearer ${authToken}` }
                    });
                    const data = await response.json();
                    document.getElementById('healthData').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    console.error('Health polling error:', error);
                }
            };
            
            updateHealth();
            setInterval(updateHealth, 10000);
        }

        async function executeCommand() {
            const command = document.getElementById('commandSelect').value;
            const output = document.getElementById('commandOutput');
            
            try {
                const response = await fetch('/execute-command', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${authToken}`
                    },
                    body: JSON.stringify({
                        command: command,
                        parameters: {}
                    })
                });
                
                const result = await response.json();
                output.textContent = JSON.stringify(result, null, 2);
            } catch (error) {
                output.textContent = `Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>