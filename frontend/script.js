'use strict';

/* ══════════════════════════════════════════════════════════════════
   MTN MoMo Analytics — Dashboard Script
   Author : Adossi Fred William — African Leadership University
   Date   : June 2025
   ══════════════════════════════════════════════════════════════════ */

/* ── Transaction type metadata ─────────────────────────────────── */
const TYPE_META = {
  'Incoming Money':    { color: '#00D68F', short: 'Incoming'    },
  'Payment':          { color: '#FF5C7A', short: 'Payment'     },
  'Bank Deposit':     { color: '#4DB6FF', short: 'Bank Dep.'   },
  'Peer Transfer':    { color: '#B57BFF', short: 'Transfer'    },
  'Airtime Purchase': { color: '#FF9550', short: 'Airtime'     },
  'Cash Withdrawal':  { color: '#FF6EB4', short: 'Withdrawal'  },
  'Direct Payment':   { color: '#00D4CC', short: 'Direct Pay'  },
};

const PER_PAGE = 50;

/* ── State ─────────────────────────────────────────────────────── */
let currentPage  = 1;
let activeType   = '';
let searchTimer  = null;
const charts     = {};

/* ══════════════════════════════════════════════════════════════════
   THEME
   ══════════════════════════════════════════════════════════════════ */
function initTheme() {
  // data-theme already set by the inline script in HTML to avoid FOUC.
  // Nothing more needed here — CSS handles icon visibility.
}

document.getElementById('themeToggle').addEventListener('click', function () {
  const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('momo-theme', next);
  // Redraw charts so colours match the new theme
  drawCharts();
});

/* ══════════════════════════════════════════════════════════════════
   FORMATTERS
   ══════════════════════════════════════════════════════════════════ */
function typeColor(type) {
  return (TYPE_META[type] || {}).color || '#8888AA';
}

function typeShort(type) {
  return (TYPE_META[type] || {}).short || type;
}

/** Compact: 31,280,396 → "31.3M RWF" — for KPI cards */
function fmtAmountCompact(n) {
  if (n == null) return '—';
  n = Number(n);
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B RWF';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M RWF';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K RWF';
  return n.toLocaleString('en-RW') + ' RWF';
}

/** Full: 1,234,567 RWF — for table and tooltips */
function fmtAmount(n) {
  if (n == null) return '—';
  return Number(n).toLocaleString('en-RW') + ' RWF';
}

function fmtDate(iso) {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleString('en-GB', { dateStyle: 'medium', timeStyle: 'short' });
  } catch (_) { return iso; }
}

function hexToRgb(hex) {
  var m = hex.match(/^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i);
  return m ? [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)] : [128, 128, 168];
}

/* ══════════════════════════════════════════════════════════════════
   ANIMATED COUNTER
   ══════════════════════════════════════════════════════════════════ */
function animateCounter(el, target, formatFn, duration) {
  if (!el) return;
  duration = duration || 1000;
  var start = performance.now();
  function tick(now) {
    var progress = Math.min((now - start) / duration, 1);
    var ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = formatFn(target * ease);
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

/* ══════════════════════════════════════════════════════════════════
   API LAYER
   ══════════════════════════════════════════════════════════════════ */
function showError(msg) {
  var el = document.getElementById('errorMsg');
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(function () { el.classList.add('hidden'); }, 7000);
}

async function apiFetch(path) {
  try {
    var res = await fetch(path);
    if (!res.ok) throw new Error('HTTP ' + res.status);
    return await res.json();
  } catch (err) {
    showError('Failed to fetch data: ' + err.message);
    throw err;
  }
}

/* ══════════════════════════════════════════════════════════════════
   KPI STATS
   ══════════════════════════════════════════════════════════════════ */
async function loadStats() {
  var s = await apiFetch('/api/stats');

  animateCounter(
    document.getElementById('statTotal'),
    s.total,
    function (v) { return Math.round(v).toLocaleString('en-RW'); }
  );
  animateCounter(
    document.getElementById('statVolume'),
    s.volume,
    fmtAmountCompact
  );
  animateCounter(
    document.getElementById('statMax'),
    s.max_tx,
    fmtAmountCompact
  );
  animateCounter(
    document.getElementById('statAvg'),
    s.avg_tx,
    fmtAmountCompact
  );
}

/* ══════════════════════════════════════════════════════════════════
   CATEGORY CHIPS
   ══════════════════════════════════════════════════════════════════ */
function buildChips(typeCounts) {
  var wrap = document.getElementById('categoryChips');

  // Remove previously generated chips (keep the static "All" chip)
  wrap.querySelectorAll('.chip:not([data-type=""])').forEach(function (c) { c.remove(); });

  Object.entries(typeCounts)
    .sort(function (a, b) { return b[1] - a[1]; })
    .forEach(function (entry) {
      var type  = entry[0];
      var count = entry[1];
      var color = typeColor(type);
      var btn   = document.createElement('button');
      btn.className    = 'chip';
      btn.dataset.type = type;
      btn.style.setProperty('--chip-color', color);

      var label = document.createElement('span');
      label.textContent = typeShort(type);
      var badge = document.createElement('span');
      badge.className   = 'chip-count';
      badge.textContent = count;
      btn.appendChild(label);
      btn.appendChild(badge);

      btn.addEventListener('click', function () { activateChip(type, btn); });
      wrap.appendChild(btn);
    });
}

function activateChip(type, btn) {
  // Reset all chips
  document.querySelectorAll('.chip').forEach(function (c) {
    c.classList.remove('active');
    c.style.removeProperty('background');
    c.style.removeProperty('border-color');
    c.style.removeProperty('color');
  });

  btn.classList.add('active');

  if (type) {
    var color = typeColor(type);
    btn.style.background   = color;
    btn.style.borderColor  = color;
    btn.style.color        = '#fff';
  }
  // "All" chip (type === '') is handled purely by CSS

  activeType = type;
  document.getElementById('searchBox').value = '';
  document.getElementById('noResultMsg').classList.add('hidden');
  loadPage(1);
}

/* ══════════════════════════════════════════════════════════════════
   TABLE
   ══════════════════════════════════════════════════════════════════ */
function makeBadge(type) {
  var color = typeColor(type);
  var rgb   = hexToRgb(color);
  var span  = document.createElement('span');
  span.className        = 'type-badge';
  span.textContent      = typeShort(type);
  span.style.color      = color;
  span.style.background = 'rgba(' + rgb[0] + ',' + rgb[1] + ',' + rgb[2] + ',0.14)';
  return span;
}

function renderRow(txn) {
  var tr = document.createElement('tr');

  var td0 = document.createElement('td');
  td0.appendChild(makeBadge(txn.type));
  tr.appendChild(td0);

  var td1 = document.createElement('td');
  td1.className   = 'amount-cell align-right';
  td1.textContent = fmtAmount(txn.amount);
  tr.appendChild(td1);

  [txn.party || '—', txn.tx_id || '—', fmtDate(txn.date)].forEach(function (val, i) {
    var td = document.createElement('td');
    td.textContent = val;
    if (i > 0) td.className = 'cell-muted';
    tr.appendChild(td);
  });

  return tr;
}

function populateTable(rows) {
  var tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  if (!rows.length) {
    var tr = document.createElement('tr');
    var td = document.createElement('td');
    td.colSpan   = 5;
    td.className = 'empty-state';
    td.textContent = 'No transactions match your filters.';
    tr.appendChild(td);
    tbody.appendChild(tr);
    return;
  }

  rows.forEach(function (txn) { tbody.appendChild(renderRow(txn)); });
}

/* ══════════════════════════════════════════════════════════════════
   PAGINATION
   ══════════════════════════════════════════════════════════════════ */
function pageRange(current, total) {
  if (total <= 7) {
    var pages = [];
    for (var i = 1; i <= total; i++) pages.push(i);
    return pages;
  }
  var out = [1];
  if (current > 3) out.push('…');
  for (var p = Math.max(2, current - 1); p <= Math.min(total - 1, current + 1); p++) out.push(p);
  if (current < total - 2) out.push('…');
  out.push(total);
  return out;
}

function renderPagination(total, page, pages) {
  var el = document.getElementById('pagination');
  el.innerHTML = '';

  document.getElementById('tableCount').textContent = total.toLocaleString('en-RW');

  if (pages <= 1) return;

  function pageBtn(label, targetPage, isActive, disabled) {
    var btn = document.createElement('button');
    btn.className   = 'page-btn' + (isActive ? ' active' : '');
    btn.textContent = label;
    btn.disabled    = !!disabled;
    if (!disabled) btn.addEventListener('click', function () { loadPage(targetPage); });
    return btn;
  }

  el.appendChild(pageBtn('←', page - 1, false, page <= 1));

  pageRange(page, pages).forEach(function (p) {
    if (p === '…') {
      var span = document.createElement('span');
      span.className   = 'page-ellipsis';
      span.textContent = '…';
      el.appendChild(span);
    } else {
      el.appendChild(pageBtn(p, p, p === page, false));
    }
  });

  el.appendChild(pageBtn('→', page + 1, false, page >= pages));

  var info = document.createElement('span');
  info.className   = 'page-info';
  info.textContent = page + ' / ' + pages;
  el.appendChild(info);
}

/* ══════════════════════════════════════════════════════════════════
   DATA LOADING
   ══════════════════════════════════════════════════════════════════ */
async function loadPage(page) {
  currentPage = page;
  var url = '/api/transactions?page=' + page + '&per_page=' + PER_PAGE;
  if (activeType) url += '&type=' + encodeURIComponent(activeType);

  var data = await apiFetch(url);
  populateTable(data.data);
  renderPagination(data.total, data.page, data.pages);
}

/* ══════════════════════════════════════════════════════════════════
   SEARCH (debounced, 350 ms)
   ══════════════════════════════════════════════════════════════════ */
async function doSearch(query) {
  if (!query) {
    document.getElementById('noResultMsg').classList.add('hidden');
    return loadPage(1);
  }

  var results = await apiFetch('/api/search?query=' + encodeURIComponent(query));
  document.getElementById('pagination').innerHTML = '';
  document.getElementById('tableCount').textContent = results.length.toLocaleString('en-RW');
  document.getElementById('noResultMsg').classList.toggle('hidden', results.length > 0);
  populateTable(results);
}

function handleSearchInput(e) {
  clearTimeout(searchTimer);
  var query = e.target.value.trim();
  // Deactivate type chips while searching
  document.querySelectorAll('.chip').forEach(function (c) {
    c.classList.remove('active');
    c.style.removeProperty('background');
    c.style.removeProperty('border-color');
    c.style.removeProperty('color');
  });
  document.querySelector('.chip[data-type=""]').classList.add('active');
  activeType = '';
  searchTimer = setTimeout(function () { doSearch(query); }, 350);
}

/* ══════════════════════════════════════════════════════════════════
   CHARTS
   ══════════════════════════════════════════════════════════════════ */
function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

function isDark() {
  return document.documentElement.getAttribute('data-theme') !== 'light';
}

function chartTheme() {
  var dark = isDark();
  return {
    grid:    dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
    text:    dark ? '#6B6B9A'               : '#5A5A90',
    tooltip: {
      bg:    dark ? '#0F0F1A' : '#FFFFFF',
      title: dark ? '#F0F0FA' : '#12122A',
      body:  dark ? '#6B6B9A' : '#5A5A90',
      border:dark ? 'rgba(255,255,255,0.09)' : 'rgba(0,0,0,0.09)',
    },
  };
}

function tooltipDefaults(theme) {
  return {
    backgroundColor: theme.tooltip.bg,
    titleColor:      theme.tooltip.title,
    bodyColor:       theme.tooltip.body,
    borderColor:     theme.tooltip.border,
    borderWidth: 1,
    padding: 12,
    cornerRadius: 8,
    displayColors: false,
  };
}

async function drawCharts() {
  var summary  = await apiFetch('/api/summary');
  var typeData  = summary.type_summary;
  var monthData = summary.monthly_summary;
  var typeCnts  = summary.type_counts;

  buildChips(typeCnts);

  var theme    = chartTheme();
  var types    = Object.keys(typeData);
  var amounts  = Object.values(typeData);
  var colors   = types.map(typeColor);
  var grandTotal = amounts.reduce(function (a, b) { return a + b; }, 0);

  document.getElementById('chartTotal').textContent = fmtAmountCompact(grandTotal);

  Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
  Chart.defaults.font.size   = 12;
  Chart.defaults.color       = theme.text;

  function fmtTick(v)  { return (v / 1e6).toFixed(1) + 'M'; }
  function fmtTip(ctx) { return '  ' + fmtAmount(ctx.raw); }

  /* ── 1. Horizontal bar chart ─────────────────────────────────── */
  destroyChart('typeChart');
  charts.typeChart = new Chart(document.getElementById('typeChart'), {
    type: 'bar',
    data: {
      labels: types,
      datasets: [{
        data: amounts,
        backgroundColor: colors.map(function (c) { return c + 'BB'; }),
        borderColor: colors,
        borderWidth: 2,
        borderRadius: 5,
        borderSkipped: false,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: Object.assign({ callbacks: { label: fmtTip } }, tooltipDefaults(theme)),
      },
      scales: {
        x: {
          grid: { color: theme.grid },
          ticks: { callback: fmtTick, color: theme.text },
          border: { display: false },
        },
        y: {
          grid: { display: false },
          ticks: { color: theme.text },
          border: { display: false },
        },
      },
    },
  });

  /* ── 2. Area / line chart (monthly) ──────────────────────────── */
  var lineCtx   = document.getElementById('monthlyChart').getContext('2d');
  var lineGrad  = lineCtx.createLinearGradient(0, 0, 0, 200);
  lineGrad.addColorStop(0,   'rgba(255,204,0,0.30)');
  lineGrad.addColorStop(0.7, 'rgba(255,204,0,0.05)');
  lineGrad.addColorStop(1,   'rgba(255,204,0,0.00)');

  destroyChart('monthlyChart');
  charts.monthlyChart = new Chart(lineCtx, {
    type: 'line',
    data: {
      labels: Object.keys(monthData),
      datasets: [{
        label: 'Volume',
        data: Object.values(monthData),
        borderColor: '#FFCC00',
        backgroundColor: lineGrad,
        fill: true,
        tension: 0.42,
        pointRadius: 4,
        pointHoverRadius: 7,
        pointBackgroundColor: '#FFCC00',
        pointBorderColor: isDark() ? '#09090F' : '#FFFFFF',
        pointBorderWidth: 2,
        borderWidth: 2.5,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: Object.assign({ callbacks: { label: fmtTip } }, tooltipDefaults(theme)),
      },
      scales: {
        x: { grid: { color: theme.grid }, ticks: { color: theme.text }, border: { display: false } },
        y: { grid: { color: theme.grid }, ticks: { callback: fmtTick, color: theme.text }, border: { display: false } },
      },
    },
  });

  /* ── 3. Doughnut chart ───────────────────────────────────────── */
  destroyChart('pieChart');
  charts.pieChart = new Chart(document.getElementById('pieChart'), {
    type: 'doughnut',
    data: {
      labels: types,
      datasets: [{
        data: amounts,
        backgroundColor: colors.map(function (c) { return c + 'CC'; }),
        borderColor: isDark() ? '#0F0F1A' : '#FFFFFF',
        borderWidth: 3,
        hoverOffset: 10,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '66%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            padding: 14,
            usePointStyle: true,
            pointStyleWidth: 8,
            font: { size: 11 },
            color: theme.text,
          },
        },
        tooltip: Object.assign({
          callbacks: {
            label: function (ctx) {
              var pct = ((ctx.raw / grandTotal) * 100).toFixed(1);
              return '  ' + fmtAmount(ctx.raw) + ' (' + pct + '%)';
            },
          },
        }, tooltipDefaults(theme)),
      },
    },
  });
}

/* ══════════════════════════════════════════════════════════════════
   CSV EXPORT
   ══════════════════════════════════════════════════════════════════ */
async function exportCSV() {
  var btn = document.getElementById('exportBtn');
  var orig = btn.innerHTML;
  btn.textContent = 'Exporting…';
  btn.disabled = true;

  try {
    var data = await apiFetch('/api/transactions?per_page=2000');
    var headers = ['Type', 'Amount (RWF)', 'Party', 'Transaction ID', 'Date'];
    var rows = data.data.map(function (t) {
      return [t.type, t.amount, t.party || '', t.tx_id || '', t.date || ''];
    });

    var csv = [headers].concat(rows)
      .map(function (row) {
        return row.map(function (v) {
          return '"' + String(v).replace(/"/g, '""') + '"';
        }).join(',');
      })
      .join('\r\n');

    var blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' });
    var url  = URL.createObjectURL(blob);
    var a    = document.createElement('a');
    a.href     = url;
    a.download = 'momo_transactions_june2025.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } finally {
    btn.innerHTML = orig;
    btn.disabled  = false;
  }
}

/* ══════════════════════════════════════════════════════════════════
   PAGE LOADER
   ══════════════════════════════════════════════════════════════════ */
function hideLoader() {
  var loader = document.getElementById('pageLoader');
  if (!loader) return;
  loader.classList.add('fade-out');
  setTimeout(function () { if (loader.parentNode) loader.parentNode.removeChild(loader); }, 500);
}

/* ══════════════════════════════════════════════════════════════════
   BOOTSTRAP
   ══════════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async function () {
  initTheme();

  /* Search */
  var searchBox = document.getElementById('searchBox');
  searchBox.addEventListener('input', handleSearchInput);
  searchBox.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { this.value = ''; doSearch(''); }
  });

  /* "All" chip click */
  document.querySelector('.chip[data-type=""]').addEventListener('click', function () {
    activateChip('', this);
  });

  /* Export */
  document.getElementById('exportBtn').addEventListener('click', exportCSV);

  /* Load all data in parallel, then hide loader */
  try {
    await Promise.all([loadStats(), drawCharts(), loadPage(1)]);
  } catch (_) {
    /* errors already shown via showError() */
  } finally {
    hideLoader();
  }
});
