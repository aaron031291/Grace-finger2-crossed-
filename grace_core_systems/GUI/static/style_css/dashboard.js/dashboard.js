let authToken = null;
let cy = null;

function initCy() {
    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: [],
        style: [{
            selector: 'node',
            style: {
                'label': 'data(id)',
                'background-color': getComputedStyle(document.documentElement).getPropertyValue('--grace-blue'),
                'text-valign': 'center',
                'width': 40,
                'height': 40
            }
        }, {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': getComputedStyle(document.documentElement).getPropertyValue('--grace-blue'),
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

        if (!response.ok) throw new Error(`Login failed: ${response.status}`);

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
            body: JSON.stringify({ command: command, parameters: {} })
        });

        const result = await response.json();
        output.textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        output.textContent = `Error: ${error.message}`;
    }
}