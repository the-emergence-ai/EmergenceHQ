const DIR_URL = 'http://127.0.0.1:8000/agents';
const filterInput = document.getElementById('filter');
const tbody = document.querySelector('#agents tbody');

async function loadAgents() {
    try {
        const res = await fetch(DIR_URL);
        const agents = await res.json();
        render(agents);
        filterInput.addEventListener('input', () => render(agents, filterInput.value));
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4">Directory unavailable</td></tr>`;
    }
}

function render(list, filter='') {
    const f = filter.toLowerCase();
    const rows = list
        .filter(a => a.name.toLowerCase().includes(f) || a.image.toLowerCase().includes(f))
        .map(a => rowHTML(a))
        .join('');
    tbody.innerHTML = rows || `<tr><td colspan="4">(no matches)</td></tr>`;
}

function rowHTML(a) {
    const statusDot = getStatusDot(a.status);
    const lastPing = a.last_ping ? 
        new Date(a.last_ping).toLocaleString() : 
        'Never';
    
    const curl = `docker pull ${a.image} && echo '{"id":"1","from":"hub","to":"${a.name}","verb":"HELP","data":{"prompt":"ping"}}' | docker run -i --rm ${a.image}`;
    
    return `
        <tr>
            <td>${statusDot} ${a.name}</td>
            <td><code>${a.image}</code></td>
            <td>${lastPing}</td>
            <td>
                <button onclick="copyCmd('${escapeQuotes(curl)}')">Copy Test Command</button>
            </td>
        </tr>
    `;
}

function getStatusDot(status) {
    let color, title;
    
    switch(status) {
        case 'healthy':
            color = '#18c964';  // Green
            title = 'Healthy - Agent responding correctly';
            break;
        case 'error':
            color = '#f31260';  // Red
            title = 'Error - Agent not responding or failing';
            break;
        default:
            color = '#d0d0d0';  // Gray
            title = 'Unknown - Health check pending';
    }
    
    return `<span 
        style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${color};margin-right:6px;" 
        title="${title}">
    </span>`;
}

function escapeQuotes(str) {
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

window.copyCmd = function(cmd) {
    navigator.clipboard.writeText(cmd).then(
        () => alert('Command copied!'),
        () => alert('Copy failed')
    );
};

// Auto-refresh every 30 seconds to show updated health status
setInterval(loadAgents, 30000);

loadAgents();