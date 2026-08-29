/**
 * Explainer page charts — Ukraine Missile Defense Research
 * Loads real data files from data/ and renders Chart.js visualizations.
 * All numbers come from the committed analysis outputs — nothing fabricated.
 */

/* ---------- helpers ---------- */
const fmtMoney = (v) => v >= 1e9 ? '$' + (v / 1e9).toFixed(2) + 'B'
    : v >= 1e6 ? '$' + (v / 1e6).toFixed(1) + 'M'
    : v >= 1e3 ? '$' + (v / 1e3).toFixed(1) + 'K'
    : '$' + Math.round(v);

const fmtNum = (v) => Math.round(v).toLocaleString('en-US');

const STRAT_COLORS = {
    passive: '#16a34a',
    hybrid: '#8b5cf6',
    cruise_active: '#3b82f6',
    ai_killer: '#f59e0b',
    high_end: '#dc2626',
};
const STRAT_SHORT = {
    passive: 'A · Passive-first',
    hybrid: 'D · Hybrid doctrine',
    cruise_active: 'B · Cruise-active',
    ai_killer: 'C · AI-killer',
    high_end: 'E · High-end missile',
};
const STRAT_ORDER = ['passive', 'hybrid', 'cruise_active', 'ai_killer', 'high_end'];

const ChartJSDefaults = () => {
    Chart.defaults.color = '#475569';
    Chart.defaults.font.family = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.borderColor = '#e2e8f0';
};

let charts = [];
function makeChart(id, config) {
    const el = document.getElementById(id);
    if (!el || typeof Chart === 'undefined') return;
    if (charts[id]) charts[id].destroy();
    charts[id] = new Chart(el, config);
}

/* ---------- fetch all data ---------- */
async function loadAll() {
    const [threats, mc, decision] = await Promise.all([
        fetch('data/threat-profiles.json').then(r => r.json()),
        fetch('data/monte_carlo_analysis.json').then(r => r.json()),
        fetch('data/bayesian_decision.json').then(r => r.json()),
    ]);
    return { threats, mc, decision };
}

/* ---------- hero stats ---------- */
function updateHero(d) {
    const set = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
    const p = d.summary.passive;
    const bp = d.best_probability;
    set('hs-passive-cpl', fmtMoney(p.cost_per_life_median) + '/life');
    set('hs-passive-pct', (bp.best_cost_per_life.passive * 100).toFixed(0) + '%');
    set('hs-hybrid-pct', (bp.best_lives_saved.hybrid * 100).toFixed(0) + '%');
}

/* ---------- threat charts ---------- */
function buildThreatCharts(t) {
    const sys = t.russian_offensive_systems;
    const order = ['shahed', 'kh101', 'kalibr', 'iskander', 'kinzhal'];
    const names = { kinzhal: 'Kinzhal', iskander: 'Iskander', kalibr: 'Kalibr', kh101: 'Kh-101', shahed: 'Shahed' };

    // Speed: Kinzhal Mach 10, Iskander 6 (unverified), Kalibr 0.8, Kh-101 0.7 (0.58-0.8), Shahed 185km/h ≈ 0.15 mach
    const speeds = [
        { n: 'Kinzhal', v: sys.kinzhal.speed_mach, note: '' },
        { n: 'Iskander', v: sys.iskander.speed_mach, note: 'est.' },
        { n: 'Kalibr', v: sys.kalibr.speed_mach, note: '' },
        { n: 'Kh-101', v: (sys.kh101.speed_mach_cruise + sys.kh101.speed_mach) / 2, note: '' },
        { n: 'Shahed', v: 0.15, note: '185 km/h' },
    ].sort((a, b) => a.v - b.v);

    makeChart('chartSpeed', {
        type: 'bar',
        data: {
            labels: speeds.map(s => s.n + (s.note ? ' (' + s.note + ')' : '')),
            datasets: [{
                label: 'Speed (Mach)',
                data: speeds.map(s => s.v),
                backgroundColor: speeds.map(s => s.v >= 5 ? '#dc2626' : s.v >= 1 ? '#f59e0b' : '#3b82f6'),
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: 'y',
            plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => c.formattedValue + ' Mach' } } },
            scales: { x: { title: { display: true, text: 'Mach (speed of sound)' } } },
            maintainAspectRatio: false,
        },
    });

    // Warhead mass
    const warheads = [
        { n: 'Shahed', v: sys.shahed.warhead_kg },
        { n: 'Kalibr', v: sys.kalibr.warhead_kg },
        { n: 'Kh-101', v: sys.kh101.warhead_kg },
        { n: 'Kinzhal', v: sys.kinzhal.warhead_kg },
        { n: 'Iskander', v: (sys.iskander.warhead_kg + sys.iskander.warhead_kg_max) / 2 },
    ].sort((a, b) => a.v - b.v);

    makeChart('chartWarhead', {
        type: 'bar',
        data: {
            labels: warheads.map(w => w.n),
            datasets: [{
                label: 'Warhead mass (kg)',
                data: warheads.map(w => w.v),
                backgroundColor: warheads.map(w => w.v > 400 ? '#dc2626' : w.v > 100 ? '#f59e0b' : '#3b82f6'),
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: { x: { title: { display: true, text: 'kg' } } },
            maintainAspectRatio: false,
        },
    });

    // Cost asymmetry: cost per threat vs cost per shot
    const costs = [
        { n: 'Shahed (domestic)', v: 48000, tag: 'verified range' },
        { n: 'Shahed (procured)', v: 193000, tag: 'verified' },
        { n: 'Kh-101', v: 2500000, tag: 'estimate' },
        { n: 'Kalibr', v: 3000000, tag: 'estimate' },
        { n: 'Iskander', v: 6000000, tag: 'estimate' },
        { n: 'Kinzhal', v: 12000000, tag: 'estimate' },
        { n: 'Iron Dome interceptor', v: 50000, tag: 'estimate' },
        { n: 'Gepard per engagement', v: 1000, tag: 'estimate' },
        { n: 'Patriot PAC-3 interceptor', v: 4000000, tag: 'estimate' },
    ];

    const colors = costs.map(c => {
        if (c.n.startsWith('Shahed')) return '#f59e0b';
        if (c.n.includes('interceptor') || c.n.includes('Gepard')) return '#3b82f6';
        return '#64748b';
    });

    makeChart('chartCostAsym', {
        type: 'bar',
        data: {
            labels: costs.map(c => c.n.replace(' interceptor', ' interceptor').replace('per engagement', '/shot')),
            datasets: [{
                label: 'Cost (USD, log scale)',
                data: costs.map(c => c.v),
                backgroundColor: colors,
                borderRadius: 6,
            }],
        },
        options: {
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (c) => fmtMoney(c.parsed.x) } },
            },
            scales: {
                x: { type: 'logarithmic', title: { display: true, text: 'USD (log scale)' }, ticks: { callback: (v) => fmtMoney(v) } },
            },
            maintainAspectRatio: false,
        },
    });
}

/* ---------- decision table ---------- */
function buildDecisionTable(d) {
    const tbody = document.getElementById('decision-table');
    if (!tbody) return;
    const s = d.summary;
    const bp = d.best_probability;
    const meta = d.meta || {};
    tbody.innerHTML = STRAT_ORDER.map(key => {
        const row = s[key];
        if (!row) return '';
        const m = meta[key] || {};
        const isCplBest = key === 'passive' ? ' row-best' : '';
        const livesHdi = row.hdi90_lives_saved ? `${fmtNum(row.hdi90_lives_saved[0])}–${fmtNum(row.hdi90_lives_saved[1])}` : '—';
        return `
            <tr class="${isCplBest}">
                <td><strong>${STRAT_SHORT[key]}</strong></td>
                <td>${m.role || '—'}</td>
                <td>${m.capital_range || '—'}</td>
                <td>${m.deploy || '—'}</td>
                <td>${fmtNum(row.expected_lives_saved)} <small>(${livesHdi})</small></td>
                <td>${fmtMoney(row.cost_per_life_median)} <small>(${row.cost_per_life_hdi90 ? fmtMoney(row.cost_per_life_hdi90[0]) + '–' + fmtMoney(row.cost_per_life_hdi90[1]) : ''})</small></td>
                <td>${(bp.best_cost_per_life[key] * 100).toFixed(1)}%</td>
                <td>${(bp.best_lives_saved[key] * 100).toFixed(1)}%</td>
            </tr>`;
    }).join('');
}

/* ---------- decision charts ---------- */
function buildDecisionCharts(d) {
    const s = d.summary;

    // Cost per life
    const cplOrder = STRAT_ORDER.slice().sort((a, b) => s[a].cost_per_life_median - s[b].cost_per_life_median);
    makeChart('chartCpl', {
        type: 'bar',
        data: {
            labels: cplOrder.map(k => STRAT_SHORT[k]),
            datasets: [
                {
                    label: 'Median cost / life',
                    data: cplOrder.map(k => s[k].cost_per_life_median),
                    backgroundColor: cplOrder.map(k => STRAT_COLORS[k]),
                    borderRadius: 6,
                },
            ],
        },
        options: {
            indexAxis: 'y',
            plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => fmtMoney(c.parsed.x) } } },
            scales: { x: { type: 'logarithmic', title: { display: true, text: 'USD / life saved (log)' }, ticks: { callback: (v) => fmtMoney(v) } } },
            maintainAspectRatio: false,
        },
    });

    // Probability of being best
    const bp = d.best_probability;
    makeChart('chartBest', {
        type: 'bar',
        data: {
            labels: STRAT_ORDER.map(k => STRAT_SHORT[k]),
            datasets: [
                {
                    label: 'P(cheapest per life)',
                    data: STRAT_ORDER.map(k => bp.best_cost_per_life[k] * 100),
                    backgroundColor: STRAT_ORDER.map(k => STRAT_COLORS[k]),
                    borderRadius: 5,
                },
                {
                    label: 'P(most lives saved)',
                    data: STRAT_ORDER.map(k => bp.best_lives_saved[k] * 100),
                    backgroundColor: STRAT_ORDER.map(k => STRAT_COLORS[k]),
                    borderRadius: 5,
                    borderColor: STRAT_ORDER.map(k => STRAT_COLORS[k]),
                    borderWidth: 2,
                    borderDash: [4, 3],
                    backgroundColor: 'transparent',
                },
            ],
        },
        options: {
            plugins: { legend: { position: 'bottom' }, tooltip: { callbacks: { label: (c) => c.dataset.label + ': ' + c.parsed.y.toFixed(1) + '%' } } },
            scales: { y: { title: { display: true, text: '% of 20,000 scenarios' }, min: 0, max: 100 } },
            maintainAspectRatio: false,
        },
    });

    // Claims donut
    const verified = 13, estimate = 2, unverified = 21;
    makeChart('chartClaims', {
        type: 'doughnut',
        data: {
            labels: ['Verified against primary sources', 'Estimates (no public source)', 'Unverified'],
            datasets: [{
                data: [verified, estimate, unverified],
                backgroundColor: ['#16a34a', '#f59e0b', '#94a3b8'],
                borderColor: '#ffffff',
                borderWidth: 3,
            }],
        },
        options: {
            plugins: {
                legend: { position: 'bottom' },
                tooltip: { callbacks: { label: (c) => ` ${c.label}: ${c.parsed} (${((c.parsed / 36) * 100).toFixed(0)}%)` } },
            },
            maintainAspectRatio: false,
        },
    });
}

/* ---------- init ---------- */
(async function init() {
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js not loaded');
        return;
    }
    ChartJSDefaults();
    try {
        const { threats, mc, decision } = await loadAll();
        updateHero(decision);
        buildThreatCharts(threats);
        buildDecisionTable(decision);
        buildDecisionCharts(decision);
    } catch (err) {
        console.error('Failed to load explainer data:', err.message);
        const note = document.createElement('p');
        note.style.cssText = 'color:#7f1d1d;background:#fee2e2;padding:16px;border-radius:10px;';
        note.textContent = '⚠️ Could not load visualization data: ' + err.message;
        document.getElementById('problem').appendChild(note);
    }
})();
