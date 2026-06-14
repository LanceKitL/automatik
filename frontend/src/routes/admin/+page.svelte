<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { getAdminDashboard } from '$lib/services/api';
  import type { AdminDashboardResponse } from '$lib/services/api';

  let data = $state<AdminDashboardResponse['data'] | null>(null);
  let loading = $state(true);
  let animatedStats = $state({ total_users: 0, total_agents: 0, total_customers: 0, open_inquiries: 0 });
  let animatedRevenue = $state(0);
  let animatedActiveSales = $state(0);

  const now = new Date();
  const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
    + ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

  function animateCount(key: keyof typeof animatedStats, target: number) {
    const step = Math.ceil(target / 40);
    const interval = setInterval(() => {
      animatedStats[key] = Math.min(animatedStats[key] + step, target);
      if (animatedStats[key] >= target) clearInterval(interval);
    }, 20);
  }

  function animateValue(setter: (v: number) => void, target: number) {
    if (target === 0) { setter(0); return; }
    const step = Math.max(Math.ceil(target / 40), 1);
    let current = 0;
    const interval = setInterval(() => {
      current = Math.min(current + step, target);
      setter(current);
      if (current >= target) clearInterval(interval);
    }, 20);
  }

  function setAnimatedRevenue(v: number) { animatedRevenue = v; }
  function setAnimatedActiveSales(v: number) { animatedActiveSales = v; }

  function statusClass(status: string | null | undefined): string {
    if (!status) return 's-default';
    const s = status.toLowerCase();
    if (s === 'confirmed') return 's-confirmed';
    if (s === 'pending') return 's-pending';
    if (s === 'cancelled') return 's-cancelled';
    if (s === 'approved') return 's-approved';
    return 's-default';
  }

  onMount(async () => {
    try {
      const res = await getAdminDashboard();
      data = res.data;
      animateCount('total_users', data.stats.total_users);
      animateCount('total_agents', data.stats.total_agents);
      animateCount('total_customers', data.stats.total_customers);
      animateCount('open_inquiries', data.stats.open_inquiries);
      animateValue(setAnimatedRevenue, data.total_revenue);
      animateValue(setAnimatedActiveSales, data.active_sales);
    } catch {
      toast.error('Failed to load dashboard.');
    } finally {
      loading = false;
    }
  });
  </script>

{#if loading}
  <div class="loading-state">
    <span class="spinner"></span>
    <p>Loading dashboard…</p>
  </div>
{:else if data}
  <div class="dash">
    <!-- Top Bar -->
    <div class="top-bar">
      <div class="logo-row">
        <div>
          <h1>Admin Dashboard</h1>
          <p class="title-subtitle">Good day, admin! What's on your mind today?</p>
        </div>
      </div>
      <span class="timestamp">{timestamp}</span>
    </div>

    <!-- Stat Cards -->
    <div class="cards">
      <div class="stat-card c1">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M16 11c1.657 0 3-1.343 3-3s-1.343-3-3-3"/><path d="M18 19c0-2.21-2.686-4-6-4s-6 1.79-6 4"/><circle cx="9" cy="7" r="4"/></svg>
        </div>
        <div class="stat-value">{animatedStats.total_users.toLocaleString()}</div>
        <div class="stat-label">Total Users</div>
      </div>
      <div class="stat-card c2">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="14" rx="2"/><path d="M7 20h10M12 4v16"/></svg>
        </div>
        <div class="stat-value">{animatedStats.total_agents.toLocaleString()}</div>
        <div class="stat-label">Agents</div>
      </div>
      <div class="stat-card c3">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/><path d="m16 11 2 2 4-4"/></svg>
        </div>
        <div class="stat-value">{animatedStats.total_customers.toLocaleString()}</div>
        <div class="stat-label">Customers</div>
      </div>
      <div class="stat-card c4">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <div class="stat-value">{animatedStats.open_inquiries.toLocaleString()}</div>
        <div class="stat-label">Open Inquiries</div>
      </div>
      <div class="stat-card c5">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
        </div>
        <div class="stat-value">₱{animatedRevenue.toLocaleString()}</div>
        <div class="stat-label">Total Revenue</div>
      </div>
      <div class="stat-card c6">
        <div class="stat-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
        </div>
        <div class="stat-value">{animatedActiveSales.toLocaleString()}</div>
        <div class="stat-label">Active Sales</div>
      </div>
    </div>

    <!-- Tables -->
    <div class="sections">
      <!-- Recent Bookings -->
      <div class="section-card">
        <div class="section-head">
          <span class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
            Recent Bookings
          </span>
          <span class="count-pill">{data.recent_bookings.length}</span>
        </div>
        {#if data.recent_bookings.length > 0}
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Type</th><th>Status</th><th>Date</th></tr>
            </thead>
            <tbody>
              {#each data.recent_bookings as b}
                <tr>
                  <td class="id-cell">{b.booking_id}</td>
                  <td>{b.booking_type ?? '—'}</td>
                  <td><span class="status-badge {statusClass(b.status)}">{b.status ?? '—'}</span></td>
                  <td>{b.created_at ?? '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <div class="empty-state">No recent bookings.</div>
        {/if}
      </div>

      <!-- Recent Warranty Claims -->
      <div class="section-card">
        <div class="section-head">
          <span class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Warranty Claims
          </span>
          <span class="count-pill">{data.recent_warranty_claims.length}</span>
        </div>
        {#if data.recent_warranty_claims.length > 0}
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Type</th><th>Status</th><th>Date</th></tr>
            </thead>
            <tbody>
              {#each data.recent_warranty_claims as w}
                <tr>
                  <td class="id-cell">{w.claim_id}</td>
                  <td>{w.claim_type ?? '—'}</td>
                  <td><span class="status-badge {statusClass(w.status)}">{w.status ?? '—'}</span></td>
                  <td>{w.submitted_at ?? '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <div class="empty-state">No recent warranty claims.</div>
        {/if}
      </div>

      <!-- Recent Sales -->
      <div class="section-card full-width">
        <div class="section-head">
          <span class="section-title">
            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
            Recent Sales
          </span>
          <span class="count-pill">{data.recent_sales.length}</span>
        </div>
        {#if data.recent_sales.length > 0}
          <table class="data-table">
            <thead>
              <tr><th>ID</th><th>Customer</th><th>Vehicle</th><th>Price</th><th>Type</th><th>Status</th><th>Date</th></tr>
            </thead>
            <tbody>
              {#each data.recent_sales as s}
                <tr>
                  <td class="id-cell">{s.sale_id}</td>
                  <td>{s.customer_name ?? '—'}</td>
                  <td>{s.brand ?? '—'} {s.model ?? '—'} ({s.year ?? '—'})</td>
                  <td>₱{Number(s.selling_price).toLocaleString()}</td>
                  <td>{s.payment_type ?? '—'}</td>
                  <td><span class="status-badge {statusClass(s.status)}">{s.status ?? '—'}</span></td>
                  <td>{s.sale_date ?? '—'}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        {:else}
          <div class="empty-state">No recent sales.</div>
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .dash {
    padding: 2rem 1.5rem;
    max-width: 1500px;
    margin: 0 auto;
    font-family: var(--font-sans);
  }

  /* ---------- Loading ---------- */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 40vh;
    gap: 1rem;
    color: var(--text-light);
    font-family: var(--font-sans);
  }
  .spinner {
    width: 28px;
    height: 28px;
    border: 2.5px solid var(--border);
    border-top-color: var(--primary);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ---------- Top Bar ---------- */
  .top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2rem;
  }
  .logo-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
  h1 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.5px;
    margin: 0;
  }
  .timestamp {
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--text-muted);
    background: var(--bg-muted);
    border: 0.5px solid var(--border);
    padding: 4px 12px;
    border-radius: 20px;
  }

  /* ---------- Stat Cards ---------- */
  .cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin-bottom: 1.75rem;
  }
  .stat-card {
    background: var(--bg-stat);
    border-radius: var(--radius-lg);
    padding: 1.1rem 1.2rem;
    position: relative;
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
  }
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.07);
  }
  .stat-card::before {
    content: '';
    position: absolute;
    top: -10px;
    right: -10px;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    opacity: 0.15;
  }
  .stat-card.c1::before { background: var(--accent); }
  .stat-card.c2::before { background: var(--primary-light); }
  .stat-card.c3::before { background: #6de0b0; }
  .stat-card.c4::before { background: #f77c7c; }
  .stat-card.c5::before { background: #f0c27a; }
  .stat-card.c6::before { background: #7ed6df; }
  .stat-icon {
    margin-bottom: 10px;
    display: flex;
  }
  .stat-card.c1 .stat-icon { color: var(--accent-dark); }
  .stat-card.c2 .stat-icon { color: var(--primary-dark); }
  .stat-card.c3 .stat-icon { color: var(--success); }
  .stat-card.c4 .stat-icon { color: var(--danger); }
  .stat-card.c5 .stat-icon { color: #d4a040; }
  .stat-card.c6 .stat-icon { color: #3498db; }
  .stat-value {
    font-size: 30px;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -1.5px;
    line-height: 1;
  }
  .stat-label {
    font-size: 11px;
    font-weight: 500;
    color: var(--text-muted);
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-top: 5px;
  }

  /* ---------- Sections ---------- */
  .sections {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .section-card {
    background: var(--bg-card);
    border: 0.5px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
  }
  .section-card.full-width {
    grid-column: 1 / -1;
  }
  .section-head {
    padding: 1rem 1.25rem 0.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 0.5px solid var(--chart-grid);
    background: var(--bg-canvas);
  }
  .section-title {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 7px;
    letter-spacing: 0.1px;
  }
  .section-title svg { color: var(--text-muted); }
  .count-pill {
    font-family: var(--font-mono);
    font-size: 10px;
    background: var(--bg-hover);
    color: var(--text-light);
    padding: 2px 9px;
    border-radius: 10px;
    border: 0.5px solid var(--border);
  }

  /* ---------- Data Table ---------- */
  .data-table {
    width: 100%;
    border-collapse: collapse;
  }
  .data-table th {
    padding: 8px 1.25rem;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
    color: var(--text-muted);
    letter-spacing: 0.7px;
    text-transform: uppercase;
    background: var(--bg-canvas);
  }
  .data-table td {
    padding: 9px 1.25rem;
    color: var(--text-light);
    border-top: 0.5px solid var(--border-lighter);
    font-family: var(--font-mono);
    font-size: 11px;
    vertical-align: middle;
  }
  .data-table tr:hover td {
    background: var(--bg-muted);
  }
  .id-cell {
    color: var(--text-primary) !important;
    font-weight: 500;
  }

  /* ---------- Status Badges ---------- */
  .status-badge {
    display: inline-block;
    padding: 2px 9px;
    border-radius: 20px;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.3px;
    font-family: var(--font-sans);
  }
  .s-pending    { background: rgba(247,199,117,0.18); color: #b8860b; }
  .s-confirmed  { background: rgba(109,224,176,0.18); color: var(--success); }
  .s-cancelled  { background: rgba(247,124,124,0.18); color: var(--danger); }
  .s-approved   { background: rgba(124,157,247,0.18); color: var(--primary-dark); }
  .s-default    { background: var(--bg-hover); color: var(--text-light); }

  /* ---------- Empty State ---------- */
  .empty-state {
    padding: 2rem 1.25rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
  }

  /* ---------- Responsive ---------- */
  @media (max-width: 720px) {
    .sections { grid-template-columns: 1fr; }
    .cards { grid-template-columns: repeat(2, 1fr); }
    .top-bar { flex-wrap: wrap; gap: 8px; }
  }
</style>