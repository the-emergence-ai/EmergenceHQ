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
    tbody.innerHTML = `<tr><td colspan="3" style="color:red">Directory unavailable</td></tr>`;
  }
}

function render(list, filter='') {
  const f = filter.toLowerCase();
  const rows = list
    .filter(a => a.name.toLowerCase().includes(f) || a.image.toLowerCase().includes(f))
    .map(a => rowHTML(a))
    .join('');
  tbody.innerHTML = rows || `<tr><td colspan="3">(no matches)</td></tr>`;
}

function rowHTML(a) {
  const curl = `docker pull ${a.image} && echo '{"id":"1","from":"hub","to":"${a.name}","verb":"HELP","data":{"prompt":"ping"}}' | docker run -i --rm ${a.image}`;
  return `
    <tr>
      <td>${a.name}</td>
      <td><code>${a.image}</code></td>
      <td><button onclick="copyCmd('${escapeQuotes(curl)}')">Copy cURL</button></td>
    </tr>`;
}

function escapeQuotes(str){
  return str.replace(/'/g,"\\'").replace(/"/g,'\\"');
}

window.copyCmd = function(cmd) {
  navigator.clipboard.writeText(cmd).then(
    () => alert('Command copied!'),
    () => alert('Copy failed')
  );
};

loadAgents();
