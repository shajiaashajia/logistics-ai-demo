const ordersInput = document.getElementById('ordersInput');
const vehiclesInput = document.getElementById('vehiclesInput');
const result = document.getElementById('result');
const assignmentRows = document.getElementById('assignmentRows');

const kpiTotal = document.getElementById('kpiTotal');
const kpiAssigned = document.getElementById('kpiAssigned');
const kpiUnassigned = document.getElementById('kpiUnassigned');
const kpiScore = document.getElementById('kpiScore');

const example = {
  orders: [
    { id: 'O-1001', pickup: [31.23, 121.47], dropoff: [31.30, 121.55], weight: 120, priority: 5, deadline_hour: 3 },
    { id: 'O-1002', pickup: [31.22, 121.45], dropoff: [31.18, 121.40], weight: 80, priority: 3, deadline_hour: 4 },
    { id: 'O-1003', pickup: [31.25, 121.42], dropoff: [31.35, 121.49], weight: 250, priority: 4, deadline_hour: 5 }
  ],
  vehicles: [
    { id: 'V-1', location: [31.21, 121.46], capacity: 300, speed_kmph: 45, available_from_hour: 0 },
    { id: 'V-2', location: [31.30, 121.52], capacity: 150, speed_kmph: 40, available_from_hour: 0 }
  ]
};

function renderAssignments(assignments) {
  assignmentRows.innerHTML = '';
  assignments.forEach((a) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${a.order_id}</td><td>${a.vehicle_id}</td><td>${a.eta_hour}</td><td>${a.travel_km}</td><td>${a.score}</td><td>${a.deadline_breached ? '是' : '否'}</td>`;
    assignmentRows.appendChild(tr);
  });
}

function renderKpis(summary, score) {
  kpiTotal.textContent = summary?.orders_total ?? 0;
  kpiAssigned.textContent = summary?.orders_assigned ?? 0;
  kpiUnassigned.textContent = summary?.orders_unassigned ?? 0;
  kpiScore.textContent = score ?? 0;
}

document.getElementById('loadExample').addEventListener('click', () => {
  ordersInput.value = JSON.stringify(example.orders, null, 2);
  vehiclesInput.value = JSON.stringify(example.vehicles, null, 2);
});

document.getElementById('runSchedule').addEventListener('click', async () => {
  try {
    const orders = JSON.parse(ordersInput.value || '[]');
    const vehicles = JSON.parse(vehiclesInput.value || '[]');
    const resp = await fetch('/api/schedule', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ orders, vehicles })
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error || `HTTP ${resp.status}`);
    }
    renderAssignments(data.assignments || []);
    renderKpis(data.summary, data.total_score);
    result.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    renderAssignments([]);
    renderKpis(null, 0);
    result.textContent = `错误: ${e.message}`;
  }
});
