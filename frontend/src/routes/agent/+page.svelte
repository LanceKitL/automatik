<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { getAgentDashboard } from '$lib/services/api';
  import type { AgentDashboardResponse } from '$lib/services/api';
  import Chart from 'chart.js/auto';

  let data    = $state<AgentDashboardResponse['data'] | null>(null);
  let loading = $state(true);

  let inquiriesCount  = $derived(data?.inquiries?.length ?? 0);
  let tasksCount      = $derived(data?.pending_tasks?.length ?? 0);
  let totalCommission = $derived(
    data?.commissions_and_sales
      ? data.commissions_and_sales.reduce((s, c) => s + Number(c.total_commission), 0)
      : 0
  );

  let avgSalePrice  = $derived(
    data?.commissions_and_sales?.length
      ? Math.round(data.commissions_and_sales.reduce((s, c) => s + Number(c.selling_price), 0) / data.commissions_and_sales.length)
      : 0
  );
  let avgCommission = $derived(
    data?.commissions_and_sales?.length
      ? Math.round(totalCommission / data.commissions_and_sales.length)
      : 0
  );
  let tasksDue = $derived(data?.pending_tasks?.filter(t => t.status === 'pending').length ?? 0);

  function formatCompactCurrency(value: number): string {
    if (value >= 1_000_000) return `₱${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `₱${(value / 1_000).toFixed(0)}K`;
    return `₱${value}`;
  }

  const now       = new Date();
  const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
    + ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

  const perfMetrics = [
    { label: 'Inquiry response rate', val: 92, color: '#6de0b0' },
    { label: 'Task completion rate',  val: 78, color: '#7c9df7' },
    { label: 'Conversion rate',       val: 41, color: '#e8c97e' },
    { label: 'Customer satisfaction', val: 88, color: '#f77c7c' },
  ];

  let chartCommCanvas: HTMLCanvasElement;
  let chartDonutCanvas: HTMLCanvasElement;

  function statusBadgeClass(s: string | undefined): string {
    const m: Record<string, string> = {
      open: 'sb-open', closed: 'sb-closed',
      pending: 'sb-pending', 'in-progress': 'sb-pending', urgent: 'sb-urgent',
    };
    return m[(s ?? '').toLowerCase()] ?? 'sb-def';
  }

  function commPct(selling: unknown, commission: unknown): string {
    const pct = (Number(commission) / Number(selling)) * 100;
    return isNaN(pct) ? '—' : pct.toFixed(1) + '%';
  }

  function getLast6Months() {
    const months: { label: string; key: string }[] = [];
    const now = new Date();
    for (let i = 5; i >= 0; i--) {
      const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
      months.push({
        label: d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
        key: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
      });
    }
    return months;
  }

  function buildTrendData() {
    const months = getLast6Months();
    return {
      labels: months.map(m => m.label),
      commission: months.map(m => {
        const found = data?.commission_trend?.find(t => t.month === m.key);
        return found ? Math.round(Number(found.total_commission)) : 0;
      }),
      revenue: months.map(m => {
        const found = data?.commission_trend?.find(t => t.month === m.key);
        return found ? Math.round(Number(found.total_revenue)) : 0;
      }),
    };
  }

  function buildCharts() {
    if (chartCommCanvas) {
      const trend = buildTrendData();

      new Chart(chartCommCanvas, {
        type: 'bar',
        data: {
          labels: trend.labels,
          datasets: [
            { label: 'Commission', data: trend.commission, backgroundColor: '#1a1a2e', borderRadius: 5, borderSkipped: false },
            { label: 'Revenue', data: trend.revenue, backgroundColor: '#e8c97e', borderRadius: 5, borderSkipped: false, yAxisID: 'y2' },
          ],
        },
        options: {
          responsive: true, maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#9ca3af' } },
            y:  { position: 'left',  grid: { color: '#f0f0f0' }, ticks: { font: { size: 10 }, color: '#9ca3af',  callback: (v: number) => '₱' + (v / 1000) + 'K' } },
            y2: { position: 'right', grid: { display: false },  ticks: { font: { size: 10 }, color: '#c9a84c', callback: (v: number) => '₱' + (v / 1000000).toFixed(1) + 'M' } },
          },
        },
      });
    }

    if (chartDonutCanvas && data) {
      const taskPending  = data.pending_tasks.filter(t => t.status === 'pending').length;
      const taskInProg   = data.pending_tasks.filter(t => t.status === 'in-progress').length;
      const inqClosed    = data.inquiries.filter(i => i.status === 'closed').length;

      new Chart(chartDonutCanvas, {
        type: 'doughnut',
        data: {
          labels: ['Pending', 'In progress', 'Closed'],
          datasets: [{
            data: [taskPending, taskInProg, inqClosed],
            backgroundColor: ['#FAEEDA', '#E6F1FB', '#EAF3DE'],
            borderColor:     ['#854F0B', '#185FA5', '#3B6D11'],
            borderWidth: 1.5,
            hoverOffset: 4,
          }],
        },
        options: {
          responsive: true, maintainAspectRatio: false, cutout: '68%',
          plugins: { legend: { display: false } },
        },
      });
    }
  }

  onMount(async () => {
    try {
      const res = await getAgentDashboard();
      data = res.data;
    } catch {
      toast.error('Failed to load dashboard.');
    } finally { loading = false; }

    await tick();
    buildCharts();
  });
</script>

<div class="page">

  <!-- Top bar -->
  <div class="top-bar">
    <div class="title-row">
      <h1>Agent Dashboard</h1>
      <p class="subtitle">Monitor and track customers repair booking.</p>
    </div>
    <span class="timestamp">{timestamp}</span>
  </div>

  {#if loading}
    <div class="loading-state"><span class="spinner"></span><p>Loading dashboard…</p></div>
  {:else if data}

    <!-- Stat cards -->
    <div class="stats-row">
      <div class="sc s1">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        <div><span class="sc-val">{inquiriesCount}</span><span class="sc-lbl">Assigned Inquiries</span></div>
      </div>
      <div class="sc s2">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        <div><span class="sc-val">{tasksCount}</span><span class="sc-lbl">Pending Tasks</span></div>
      </div>
      <div class="sc s3">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
        <div><span class="sc-val">{formatCompactCurrency(totalCommission)}</span><span class="sc-lbl">Total Commission</span></div>
      </div>
    </div>

    <!-- Analytics row -->
    <div class="grid-2 gap-sm">

      <!-- Commission chart -->
      <div class="card" style="grid-column: span 2">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
            Commission trend
          </span>
          <span class="pill pill-gold">Last 6 months</span>
        </div>
        <div class="chart-wrap" style="height: 180px; position: relative">
          <canvas bind:this={chartCommCanvas} role="img" aria-label="Bar chart of monthly commission and revenue over 6 months">Monthly commission and revenue trends.</canvas>
        </div>
        <div style="display:flex;gap:14px;padding:.5rem 1.1rem .75rem;font-size:11px;color:#6b7280">
          <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:2px;background:#1a1a2e;display:inline-block"></span>Commission</span>
          <span style="display:flex;align-items:center;gap:5px"><span style="width:9px;height:9px;border-radius:2px;background:#e8c97e;display:inline-block"></span>Revenue</span>
        </div>
      </div>

      <!-- Performance -->
      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            Performance metrics
          </span>
        </div>
        <div class="perf-list">
          {#each perfMetrics as m}
            <div class="perf-row">
              <span class="perf-label">{m.label}</span>
              <div class="perf-bar-bg"><div class="perf-bar" style="width:{m.val}%;background:{m.color}"></div></div>
              <span class="perf-val">{m.val}%</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- KPIs + Donut -->
      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
            Sales KPIs
          </span>
        </div>
        <div class="mini-kpi-grid">
          <div class="mini-kpi">
            <div class="mk-val">{data.commissions_and_sales.length}</div>
            <div class="mk-lbl">Total Sales</div>
            <div class="mk-delta delta-up">This month</div>
          </div>
          <div class="mini-kpi">
            <div class="mk-val">{formatCompactCurrency(avgSalePrice)}</div>
            <div class="mk-lbl">Avg Sale Price</div>
            <div class="mk-delta delta-up">Above target</div>
          </div>
          <div class="mini-kpi">
            <div class="mk-val">{formatCompactCurrency(avgCommission)}</div>
            <div class="mk-lbl">Avg Commission</div>
            <div class="mk-delta delta-up">4% rate avg</div>
          </div>
          <div class="mini-kpi">
            <div class="mk-val">{tasksDue}</div>
            <div class="mk-lbl">Tasks Due</div>
            <div class="mk-delta delta-warn">This week</div>
          </div>
        </div>
        <div style="padding:.5rem 1rem;display:flex;justify-content:center;height:100px;position:relative">
          <canvas bind:this={chartDonutCanvas} role="img" aria-label="Donut chart of task and inquiry statuses">Task status breakdown.</canvas>
        </div>
      </div>
    </div>

    <!-- Inquiries + Tasks -->
    <div class="grid-2 gap-sm">
      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            Inquiries
          </span>
          <span class="pill">{inquiriesCount}</span>
        </div>
        {#if data.inquiries.length > 0}
          <table>
            <thead><tr><th>ID</th><th>Message</th><th>Status</th></tr></thead>
            <tbody>
              {#each data.inquiries as i}
                <tr>
                  <td class="cell-id">{i.inquiry_id ?? i.id}</td>
                  <td class="cell-msg">{(i.message ?? '').slice(0, 52)}{(i.message ?? '').length > 52 ? '…' : ''}</td>
                  <td><span class="sbadge {statusBadgeClass(i.status)}"><span class="sdot"></span>{i.status ?? '—'}</span></td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <p class="empty-state">No assigned inquiries.</p>
        {/if}
      </div>

      <div class="card">
        <div class="card-head">
          <span class="card-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
            Pending Tasks
          </span>
          <span class="pill">{tasksCount}</span>
        </div>
        {#if data.pending_tasks.length > 0}
          <table>
            <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Due</th></tr></thead>
            <tbody>
              {#each data.pending_tasks as t}
                <tr>
                  <td class="cell-id">{t.task_id ?? t.id}</td>
                  <td class="cell-name">{t.task_type ?? '—'}</td>
                  <td><span class="sbadge {statusBadgeClass(t.status)}"><span class="sdot"></span>{t.status ?? '—'}</span></td>
                  <td class="cell-mono">{t.due_date ?? '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <p class="empty-state">No pending tasks.</p>
        {/if}
      </div>
    </div>

    <!-- Commissions table -->
    <div class="card" style="margin-top: 14px">
      <div class="card-head">
        <span class="card-title">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>
          Commissions & Sales
        </span>
        <span class="pill">{data.commissions_and_sales.length}</span>
      </div>
      {#if data.commissions_and_sales.length > 0}
        <table>
          <thead><tr><th>Sale ID</th><th>Selling Price</th><th>Commission</th><th>Commission %</th></tr></thead>
          <tbody>
            {#each data.commissions_and_sales as c}
              <tr>
                <td class="cell-id">{c.sale_id}</td>
                <td class="cell-mono">₱{Number(c.selling_price).toLocaleString()}</td>
                <td class="cell-green">₱{Number(c.total_commission).toLocaleString()}</td>
                <td class="cell-blue">{commPct(c.selling_price, c.total_commission)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      {:else}
        <p class="empty-state">No sales yet.</p>
      {/if}
    </div>

  {/if}
</div>

<style>
  .page { font-family: var(--font-sans); padding: 2rem; max-width: 1500px; margin: 0 auto; }

  /* Top bar */
  .top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
  .title-row { display: flex; flex-direction: column; align-items: start; justify-content: start; margin-bottom: 10px; gap: 10px; }
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
  .logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
  h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
  .timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

  /* Loading */
  .loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
  .spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }

  /* Stat cards */
  .stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 1.25rem; }
  .sc { background: var(--bg-stat); border-radius: 12px; padding: .9rem 1.1rem; display: flex; align-items: center; gap: 12px; position: relative; overflow: hidden; transition: transform .18s; }
  .sc:hover { transform: translateY(-2px); }
  .sc::before { content: ''; position: absolute; top: -10px; right: -10px; width: 56px; height: 56px; border-radius: 50%; opacity: .12; }
  .sc.s1::before { background: var(--accent); } .sc.s2::before { background: var(--primary-light); } .sc.s3::before { background: #6de0b0; }
  .sc svg { flex-shrink: 0; }
  .sc.s1 svg { color: var(--accent-dark); } .sc.s2 svg { color: var(--primary-dark); } .sc.s3 svg { color: var(--success); }
  .sc div { display: flex; flex-direction: column; }
  .sc-val { font-size: 26px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
  .sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; margin-top: 3px; }

  /* Layout grids */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
  .gap-sm { gap: 12px; }

  /* Cards */
  .card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
  .card-head { padding: .9rem 1.1rem .7rem; display: flex; align-items: center; justify-content: space-between; border-bottom: .5px solid var(--chart-grid); background: var(--bg-canvas); }
  .card-title { font-size: 12px; font-weight: 600; color: var(--text-primary); display: flex; align-items: center; gap: 7px; }
  .card-title svg { color: var(--text-muted); }
  .pill { font-family: var(--font-mono); font-size: 10px; background: var(--bg-hover); color: var(--text-light); padding: 2px 8px; border-radius: 10px; border: 0.5px solid var(--border); }
  .pill-gold { background: var(--primary); color: var(--accent); border-color: var(--primary); }
  .chart-wrap { padding: .75rem 1rem 1rem; }

  /* Performance bars */
  .perf-list { padding: .25rem 0; }
  .perf-row { display: flex; align-items: center; gap: 10px; padding: .65rem 1.1rem; border-top: .5px solid var(--border-lighter); }
  .perf-row:first-child { border-top: none; }
  .perf-label { font-size: 11px; color: var(--text-light); min-width: 130px; }
  .perf-bar-bg { flex: 1; height: 6px; background: var(--chart-grid); border-radius: 3px; overflow: hidden; }
  .perf-bar { height: 100%; border-radius: 3px; }
  .perf-val { font-family: var(--font-mono); font-size: 11px; color: var(--text-primary); font-weight: 600; min-width: 36px; text-align: right; }

  /* KPI mini grid */
  .mini-kpi-grid { display: grid; grid-template-columns: 1fr 1fr; }
  .mini-kpi { padding: .75rem 1rem; border-right: .5px solid var(--chart-grid); border-bottom: .5px solid var(--chart-grid); }
  .mini-kpi:nth-child(2n) { border-right: none; }
  .mini-kpi:nth-last-child(-n+2) { border-bottom: none; }
  .mk-val { font-size: 18px; font-weight: 700; color: var(--text-primary); letter-spacing: -.5px; line-height: 1; }
  .mk-lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: .5px; margin-top: 3px; }
  .mk-delta { font-size: 10px; margin-top: 4px; display: inline-flex; align-items: center; gap: 2px; padding: 1px 6px; border-radius: 10px; }
  .delta-up   { background: var(--success-bg); color: var(--success-text); }
  .delta-warn { background: var(--warning-bg); color: var(--warning-text); }

  /* Tables */
  table { width: 100%; border-collapse: collapse; }
  th { padding: 7px 1rem; text-align: left; font-size: 10px; font-weight: 600; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; background: var(--bg-canvas); border-bottom: .5px solid var(--chart-grid); }
  td { padding: 8px 1rem; font-size: 11px; color: var(--text-light); border-top: .5px solid var(--border-lighter); vertical-align: middle; }
  tr:hover td { background: var(--bg-canvas); }
  .cell-id    { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); }
  .cell-name  { font-size: 12px; font-weight: 600; color: var(--text-primary); }
  .cell-msg   { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .cell-mono  { font-family: var(--font-mono); font-size: 11px; }
  .cell-green { font-family: var(--font-mono); font-size: 11px; color: var(--success); font-weight: 600; }
  .cell-blue  { font-family: var(--font-mono); font-size: 11px; color: var(--primary-dark); }
  .empty-state { padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 12px; }

  /* Status badges */
  .sbadge { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 20px; font-size: 10px; font-weight: 600; }
  .sdot { width: 5px; height: 5px; border-radius: 50%; }
  .sb-open     { background: var(--info-bg); color: var(--info-text); }
  .sb-open     .sdot { background: var(--info); }
  .sb-closed   { background: var(--success-bg); color: var(--success-text); }
  .sb-closed   .sdot { background: var(--success-dark); }
  .sb-pending  { background: var(--warning-bg); color: var(--warning-text); }
  .sb-pending  .sdot { background: var(--warning-dark); }
  .sb-urgent   { background: var(--danger-bg); color: var(--danger-text); }
  .sb-urgent   .sdot { background: var(--danger); }
  .sb-def      { background: var(--bg-hover); color: var(--text-light); }
  .sb-def      .sdot { background: #888; }

  @media (max-width: 680px) {
    .stats-row { grid-template-columns: 1fr; }
    .grid-2    { grid-template-columns: 1fr; }
  }
</style>