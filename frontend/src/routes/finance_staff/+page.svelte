<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { getFinanceDashboard } from '$lib/services/api';
  import type { FinanceDashboardResponse } from '$lib/services/api';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';
  import Chart from 'chart.js/auto';

  let data    = $state<FinanceDashboardResponse['data'] | null>(null);
  let loading = $state(true);

  const now       = new Date();
  const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
    + ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

  const monthLabels       = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
  const collectionTrend   = [9800000, 11200000, 10500000, 13100000, 11800000, 0];
  const TARGET_MONTHLY    = 11500000;

  const healthMetrics = [
    { label: 'Collection rate',    val: 96, color: '#6de0b0' },
    { label: 'Loan approval rate', val: 72, color: '#7c9df7' },
    { label: 'Portfolio quality',  val: 84, color: '#e8c97e' },
    { label: 'Process turnaround', val: 68, color: '#b5d4f4' },
  ];

  const paymentMethods = [
    { label: 'Bank Transfer', pct: 52, color: '#185FA5' },
    { label: 'Cash',          pct: 30, color: '#3B6D11' },
    { label: 'Online',        pct: 18, color: '#854F0B' },
  ];

  let chartCanvas: HTMLCanvasElement;
  let chartInstance: Chart | null = null;

  function isDelinquent(rate: unknown): boolean {
    return Number(rate) > 3;
  }

  function methodBadgeClass(m: string | undefined): string {
    const s = (m ?? '').toLowerCase();
    if (s === 'cash')          return 'sb-cash';
    if (s.startsWith('bank'))  return 'sb-bank';
    if (s === 'online')        return 'sb-online';
    return 'sb-def';
  }

  function buildChart() {
    if (!chartCanvas || !data) return;
    chartInstance?.destroy();

    const trend = [...collectionTrend];
    trend[5] = Number(data.total_collected);

    chartInstance = new Chart(chartCanvas, {
      type: 'line',
      data: {
        labels: monthLabels,
        datasets: [
          {
            label: 'Collected',
            data: trend,
            borderColor: '#1a1a2e',
            backgroundColor: '#f8f7f4',
            pointBackgroundColor: '#1a1a2e',
            pointRadius: 4,
            borderWidth: 2,
            tension: 0.35,
            fill: true,
          },
          {
            label: 'Target',
            data: Array(6).fill(TARGET_MONTHLY),
            borderColor: '#e8c97e',
            borderDash: [5, 4],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: (ctx: any) => '₱' + (ctx.raw / 1000000).toFixed(2) + 'M' } },
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af' } },
          y: { grid: { color: '#f0f0f0' }, ticks: { font: { size: 10 }, color: '#9ca3af', callback: (v: number) => '₱' + (v / 1000000).toFixed(1) + 'M' } },
        },
      },
    });
  }

  onMount(async () => {
    try {
      const res = await getFinanceDashboard();
      data = res.data;
    } catch {
      toast.error('Failed to load dashboard data.');
    }
    finally { loading = false; }

    await tick();
    buildChart();
  });
</script>

<div class="page">

  <!-- Top bar -->
  <div class="top-bar">
    <div class="title-row">
      <h1>Finance & Insurance</h1>
      <span style="color:var(--text-muted); margin-top:4px; font-size:14px">Hi there! feeling productive today?</span>
    </div>
    <span class="timestamp">{timestamp}</span>
  </div>

  {#if loading}
    <div class="loading-state"><span class="spinner"></span><p>Loading dashboard…</p></div>
  {:else if data}

    <!-- Stat cards -->
    <div class="stats-row">

      <!-- Pending reviews — clickable -->
      <div class="sc s1 clickable" onclick={() => goto('/finance_staff/loans?tab=pending')} role="button" tabindex="0">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><path d="m9 12 2 2 4-4"/></svg>
        <div class="sc-val">{data.pending_reviews}</div>
        <div class="sc-lbl">Pending Reviews</div>
        <div class="sc-sub">
          <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          Click to process
        </div>
      </div>

      <!-- Pending payments — clickable -->
      <div class="sc s1 clickable" onclick={() => goto('/finance_staff/payments')} role="button" tabindex="0">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
        <div class="sc-val">{data.pending_payments}</div>
        <div class="sc-lbl">Pending Payments</div>
        <div class="sc-sub">
          <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          Verify now
        </div>
      </div>

      <div class="sc s2">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        <div class="sc-val">{data.approved_contracting}</div>
        <div class="sc-lbl">Approved / Contracting</div>
        <div class="sc-sub">This cycle</div>
      </div>

      <div class="sc s3">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <div class="sc-val">₱{(Number(data.total_financed_portfolio) / 1000000).toFixed(1)}M</div>
        <div class="sc-lbl">Financed Portfolio</div>
        <div class="sc-sub">Active loans</div>
      </div>

      <!-- Delinquency — dynamic danger/safe -->
      <div class="sc {isDelinquent(data.delinquency_rate) ? 's-danger' : 's-safe'}">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><path d="m10.29 3.86-8.28 14.36A2 2 0 0 0 3.74 21h16.52a2 2 0 0 0 1.73-3l-8.28-14.14a2 2 0 0 0-3.46.03z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <div class="sc-val">{Number(data.delinquency_rate).toFixed(1)}%</div>
        <div class="sc-lbl">Delinquency Rate</div>
        <div class="sc-sub">
          {#if isDelinquent(data.delinquency_rate)}
            Exceeds 3% threshold
          {:else}
            Within threshold
          {/if}
        </div>
      </div>

      <div class="sc s4">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" class="sc-icon" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
        <div class="sc-val">₱{(Number(data.total_collected) / 1000000).toFixed(1)}M</div>
        <div class="sc-lbl">Total Collected</div>
        <div class="sc-sub">This month</div>
      </div>
    </div>

    <!-- Action strip -->
    {#if data.pending_reviews > 0}
      <div class="action-strip">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e8c97e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
        <p>{data.pending_reviews} loan application{data.pending_reviews > 1 ? 's' : ''} pending your review</p>
        <button class="action-btn" onclick={() => goto('/finance_staff/loans?tab=pending')}>
          Process Next Review →
        </button>
      </div>
    {/if}

    <!-- Analytics row -->
    <div class="grid-analytics">

      <!-- Collection chart -->
      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Monthly collections vs target
          </span>
          <span class="pill pill-gold">Last 6 months</span>
        </div>
        <div class="chart-wrap" style="height: 190px; position: relative">
          <canvas bind:this={chartCanvas} role="img" aria-label="Line chart comparing monthly collections against the target of ₱11.5M over 6 months">Monthly collections vs target data.</canvas>
        </div>
        <div class="chart-legend">
          <span><span class="legend-sq" style="background:#1a1a2e"></span>Collected</span>
          <span><span class="legend-sq legend-dashed"></span>Target</span>
        </div>
      </div>

      <!-- KPI + method breakdown -->
      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
            Portfolio KPIs
          </span>
        </div>
        <div class="kpi-grid">
          <div class="kpi"><div class="kv">48</div><div class="kl">Active Loans</div><div class="kd du">+3 this month</div></div>
          <div class="kpi"><div class="kv">₱1.0M</div><div class="kl">Avg Loan Size</div><div class="kd dn">Stable</div></div>
          <div class="kpi"><div class="kv">96.2%</div><div class="kl">Collection Rate</div><div class="kd du">Above 95% KPI</div></div>
          <div class="kpi"><div class="kv">3</div><div class="kl">Overdue Accounts</div><div class="kd dw">Needs follow-up</div></div>
        </div>
        <div class="method-section">
          <div class="method-title">Payment method breakdown</div>
          {#each paymentMethods as m}
            <div class="method-row">
              <div class="method-meta"><span>{m.label}</span><span class="method-pct">{m.pct}%</span></div>
              <div class="bar-bg"><div class="bar-fill" style="width:{m.pct}%;background:{m.color}"></div></div>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <!-- Bottom row: payments table + health bars -->
    <div class="grid-bottom">

      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            Recent Payments
          </span>
          <span class="pill">{data.recent_payments.length}</span>
        </div>
        {#if data.recent_payments.length > 0}
          <table>
            <thead><tr><th>ID</th><th>Customer</th><th>Amount</th><th>Method</th><th>Date</th></tr></thead>
            <tbody>
              {#each data.recent_payments as p}
                <tr>
                  <td class="cell-id">{p.payment_id}</td>
                  <td class="cell-name">{p.customer_name ?? '—'}</td>
                  <td class="cell-green">₱{Number(p.amount_paid).toLocaleString()}</td>
                  <td><span class="sbadge {methodBadgeClass(p.payment_method as string)}">{p.payment_method ?? '—'}</span></td>
                  <td class="cell-mono">{p.payment_date ? String(p.payment_date).slice(0, 10) : '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <p class="empty-state">No recent payments.</p>
        {/if}
      </div>

      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            Finance health
          </span>
        </div>
        <div class="health-list">
          {#each healthMetrics as m}
            <div class="perf-row">
              <span class="perf-label">{m.label}</span>
              <div class="perf-bar-bg"><div class="perf-bar" style="width:{m.val}%;background:{m.color}"></div></div>
              <span class="perf-val">{m.val}%</span>
            </div>
          {/each}
        </div>
      </div>
    </div>

  {/if}
</div>

<style>
  .page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

  /* Top bar */
  .top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
  .title-row { display: flex; align-items: center; gap: 10px; flex-direction: column; align-items: start; }
  .logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
  h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0; }
  .timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

  /* Loading */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }

  /* Stat cards */
  .stats-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; margin-bottom: 1.1rem; }
  .sc { background: var(--bg-stat); border-radius: 12px; padding: .85rem 1rem; position: relative; overflow: hidden; transition: transform .18s; }
  .sc.clickable { cursor: pointer; }
  .sc:hover { transform: translateY(-2px); }
  .sc::before { content: ''; position: absolute; top: -10px; right: -10px; width: 52px; height: 52px; border-radius: 50%; opacity: .12; }
  .sc.s1::before { background: var(--accent); } .sc.s2::before { background: var(--primary-light); }
  .sc.s3::before { background: #6de0b0; } .sc.s4::before { background: #b5d4f4; }
  .sc.s-danger::before { background: #f77c7c; } .sc.s-safe::before { background: #6de0b0; }
  .sc-icon { display: block; margin-bottom: 8px; }
  .sc.s1 .sc-icon { color: var(--accent-dark); } .sc.s2 .sc-icon { color: var(--primary-dark); }
  .sc.s3 .sc-icon { color: var(--success); } .sc.s4 .sc-icon { color: var(--primary-dark); }
  .sc.s-danger .sc-icon { color: var(--danger); } .sc.s-safe .sc-icon { color: var(--success); }
  .sc-val { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -.5px; line-height: 1; }
  .sc.s-danger .sc-val { color: var(--danger); } .sc.s-safe .sc-val { color: var(--success-text); }
  .sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; margin-top: 3px; }
  .sc-sub { font-size: 10px; margin-top: 5px; display: inline-flex; align-items: center; gap: 3px; padding: 2px 7px; border-radius: 10px; }
  .sc.s1 .sc-sub { background: var(--primary); color: var(--accent); }
  .sc.s-danger .sc-sub { background: var(--danger-bg); color: var(--danger-text); }
  .sc.s-safe .sc-sub { background: var(--success-bg); color: var(--success-text); }
  .sc.s2 .sc-sub, .sc.s3 .sc-sub, .sc.s4 .sc-sub { background: var(--bg-hover); color: var(--text-light); }

  /* Action strip */
  .action-strip { display: flex; align-items: center; gap: 10px; margin-bottom: 1.1rem; background: var(--primary); border-radius: 10px; padding: .75rem 1rem; }
  .action-strip p { font-size: 12px; color: var(--accent); font-weight: 600; flex: 1; margin: 0; }
  .action-btn { height: 30px; padding: 0 14px; background: var(--accent); color: var(--text-primary); border: none; border-radius: 7px; font-family: var(--font-sans); font-size: 11px; font-weight: 700; cursor: pointer; white-space: nowrap; }
  .action-btn:hover { opacity: .85; }

  /* Layout grids */
  .grid-analytics { display: grid; grid-template-columns: 1.4fr 1fr; gap: 12px; margin-bottom: 12px; }
  .grid-bottom    { display: grid; grid-template-columns: 1.4fr 1fr; gap: 12px; }

  /* Cards */
  .card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
  .card-head { padding: .85rem 1.1rem .7rem; display: flex; align-items: center; justify-content: space-between; border-bottom: .5px solid var(--chart-grid); background: var(--bg-canvas); }
  .card-title { font-size: 12px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 7px; }
  .card-title svg { color: var(--text-muted); }
  .pill { font-family: var(--font-mono); font-size: 10px; background: var(--bg-hover); color: var(--text-light); padding: 2px 8px; border-radius: 10px; border: .5px solid var(--border); }
  .pill-gold { background: var(--primary); color: var(--accent); border-color: var(--primary); }
  .chart-wrap { padding: .7rem 1rem 1rem; }
  .chart-legend { display: flex; gap: 14px; padding: .4rem 1rem .75rem; font-size: 11px; color: var(--text-light); }
  .chart-legend span { display: flex; align-items: center; gap: 5px; }
  .legend-sq { width: 9px; height: 9px; border-radius: 2px; display: inline-block; }
  .legend-dashed { background: var(--accent); }

  /* KPI grid */
  .kpi-grid { display: grid; grid-template-columns: 1fr 1fr; }
  .kpi { padding: .7rem .9rem; border-right: .5px solid var(--chart-grid); border-bottom: .5px solid var(--chart-grid); }
  .kpi:nth-child(2n) { border-right: none; }
  .kpi:nth-last-child(-n+2) { border-bottom: none; }
  .kv { font-size: 17px; font-weight: 700; color: var(--text-primary); letter-spacing: -.5px; line-height: 1; }
  .kl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 2px; }
  .kd { font-size: 10px; margin-top: 4px; display: inline-flex; align-items: center; gap: 2px; padding: 1px 6px; border-radius: 10px; }
  .du { background: var(--success-bg); color: var(--success-text); } .dw { background: var(--danger-bg); color: var(--danger-text); } .dn { background: var(--bg-hover); color: var(--text-light); }

  /* Payment methods */
  .method-section { padding: .6rem 1rem .75rem; border-top: .5px solid var(--chart-grid); }
  .method-title { font-size: 11px; font-weight: 600; color: var(--text-primary); margin-bottom: .5rem; }
  .method-row { margin-bottom: 6px; }
  .method-meta { display: flex; justify-content: space-between; font-size: 10px; color: var(--text-light); margin-bottom: 3px; }
  .method-pct { font-family: var(--font-mono); color: var(--text-primary); font-weight: 600; }
  .bar-bg { height: 5px; background: var(--chart-grid); border-radius: 3px; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 3px; }

  /* Health bars */
  .health-list { padding: .25rem 0; }
  .perf-row { display: flex; align-items: center; gap: 8px; padding: .6rem 1rem; border-top: .5px solid var(--border-lighter); }
  .perf-row:first-child { border-top: none; }
  .perf-label { font-size: 11px; color: var(--text-light); min-width: 115px; }
  .perf-bar-bg { flex: 1; height: 5px; background: var(--chart-grid); border-radius: 3px; overflow: hidden; }
  .perf-bar { height: 100%; border-radius: 3px; }
  .perf-val { font-family: var(--font-mono); font-size: 11px; color: var(--text-primary); font-weight: 600; min-width: 36px; text-align: right; }

  /* Tables */
  table { width: 100%; border-collapse: collapse; }
  th { padding: 7px 1rem; text-align: left; font-size: 10px; font-weight: 600; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; background: var(--bg-canvas); border-bottom: .5px solid var(--chart-grid); }
  td { padding: 8px 1rem; font-size: 11px; color: var(--text-light); border-top: .5px solid var(--border-lighter); vertical-align: middle; }
  tr:hover td { background: var(--bg-canvas); }
  .cell-id   { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  .cell-name { font-size: 12px; font-weight: 600; color: var(--text-primary); }
  .cell-green { font-family: var(--font-mono); font-size: 11px; color: var(--success); font-weight: 600; }
  .cell-mono  { font-family: var(--font-mono); font-size: 11px; }
  .empty-state { padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 12px; }

  /* Status badges */
  .sbadge { display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; }
  .sb-cash   { background: var(--success-bg); color: var(--success-text); }
  .sb-bank   { background: var(--info-bg); color: var(--info-text); }
  .sb-online { background: var(--warning-bg); color: var(--warning-text); }
  .sb-def    { background: var(--bg-hover); color: var(--text-light); }

  @media (max-width: 900px) {
    .stats-row { grid-template-columns: repeat(3, 1fr); }
    .grid-analytics, .grid-bottom { grid-template-columns: 1fr; }
  }
  @media (max-width: 540px) {
    .stats-row { grid-template-columns: 1fr 1fr; }
  }
</style>