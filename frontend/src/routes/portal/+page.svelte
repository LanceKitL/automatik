<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerDashboard, type CustomerDashboardResponse } from '$lib/services/api';
	import { toast } from 'svelte-sonner';

	let data = $state<CustomerDashboardResponse['data'] | null>(null);
	let loading = $state(true);

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	onMount(async () => {
		try {
			const res = await getCustomerDashboard();
			data = res.data;
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
				<h1>Dashboard</h1>
			</div>
			<span class="timestamp">{timestamp}</span>
		</div>

		<!-- Stat Cards -->
		<div class="cards">
			<div class="stat-card c1">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
				</div>
				<div class="stat-value">{data.dashboard.my_vehicles?.length ?? 0}</div>
				<div class="stat-label">My Vehicles</div>
			</div>
			<div class="stat-card c2">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>
				</div>
				<div class="stat-value">{data.dashboard.active_sales}</div>
				<div class="stat-label">Active Amortization</div>
			</div>
			<div class="stat-card c3">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
				</div>
				<div class="stat-value">{data.dashboard.open_inquiries}</div>
				<div class="stat-label">Open Inquiries</div>
			</div>
			<div class="stat-card c4">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
				</div>
				<div class="stat-value">{data.dashboard.unread_notification}</div>
				<div class="stat-label">Notifications</div>
			</div>
			<div class="stat-card c5">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
				</div>
				<div class="stat-value">₱{Number(data.dashboard.next_payment_amount ?? 0).toLocaleString()}</div>
				<div class="stat-label">Next Payment</div>
			</div>
			<div class="stat-card c6">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
				</div>
				<div class="stat-value">{data.dashboard.next_payment_due ? String(data.dashboard.next_payment_due).slice(0, 10) : '—'}</div>
				<div class="stat-label">Due Date</div>
			</div>
		</div>

		<!-- Sections -->
		<div class="sections">
			<!-- Payment Overview -->
			<div class="section-card">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>
						Payment Overview
					</span>
				</div>
				{#if data.dashboard.next_payment_due}
					<div class="payment-detail">
						<div class="payment-row">
							<span class="pay-label">Amount Due</span>
							<span class="pay-value">₱{Number(data.dashboard.next_payment_amount).toLocaleString()}</span>
						</div>
						<div class="payment-row">
							<span class="pay-label">Due Date</span>
							<span class="pay-value">{String(data.dashboard.next_payment_due).slice(0, 10)}</span>
						</div>
					</div>
				{:else}
					<div class="empty-state">No upcoming payments.</div>
				{/if}
			</div>

			<!-- My Vehicles -->
			<div class="section-card">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
						My Vehicles
					</span>
					<span class="count-pill">{data.dashboard.my_vehicles?.length ?? 0}</span>
				</div>
				{#if data.dashboard.my_vehicles?.length > 0}
					<table class="data-table">
						<thead>
							<tr><th>Vehicle</th><th>Year</th><th>Color</th></tr>
						</thead>
						<tbody>
							{#each data.dashboard.my_vehicles as v}
								<tr>
									<td class="id-cell">{v.brand ?? '—'} {v.model ?? '—'}</td>
									<td>{v.year ?? '—'}</td>
									<td>{v.color ?? '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<div class="empty-state">No vehicles yet.</div>
				{/if}
			</div>

			<!-- Recent Documents -->
			<div class="section-card full-width">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
						Recent Documents
					</span>
					<span class="count-pill">{data.dashboard.recent_documents?.length ?? 0}</span>
				</div>
				{#if data.dashboard.recent_documents?.length > 0}
					<table class="data-table">
						<thead>
							<tr><th>Document</th><th>Date</th></tr>
						</thead>
						<tbody>
							{#each data.dashboard.recent_documents as d}
								<tr>
									<td class="id-cell">{d.document_name ?? d.name ?? `#${d.document_id ?? d.id}`}</td>
									<td>{d.created_at ? String(d.created_at).slice(0, 10) : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<div class="empty-state">No documents yet.</div>
				{/if}
			</div>

			<!-- Recent Notifications -->
			<div class="section-card full-width">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
						Recent Notifications
					</span>
					<span class="count-pill">{data.notifications?.length ?? 0}</span>
				</div>
				{#if data.notifications?.length > 0}
					<div class="notif-list">
						{#each data.notifications.slice(0, 5) as n}
							<div class="notif-item">
								<span class="notif-dot" class:unread={!n.is_read}></span>
								<div class="notif-content">
									<div class="notif-title">{n.title}</div>
									<div class="notif-msg">{n.message}</div>
								</div>
							</div>
						{/each}
					</div>
				{:else}
					<div class="empty-state">No notifications.</div>
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
		font-size: 22px;
		font-weight: 700;
		color: var(--text-primary);
		letter-spacing: -1px;
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

	/* ---------- Payment Detail ---------- */
	.payment-detail {
		padding: 1rem 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 10px;
	}
	.payment-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}
	.pay-label {
		font-size: 12px;
		color: var(--text-muted);
	}
	.pay-value {
		font-family: var(--font-mono);
		font-size: 13px;
		font-weight: 700;
		color: var(--text-primary);
	}

	/* ---------- Notifications ---------- */
	.notif-list {
		padding: 4px 1.25rem;
	}
	.notif-item {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		padding: 10px 0;
		border-bottom: 0.5px solid var(--border-lighter);
	}
	.notif-item:last-child { border-bottom: none; }
	.notif-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #d1d5db;
		flex-shrink: 0;
		margin-top: 4px;
	}
	.notif-dot.unread { background: var(--blue, #3b82f6); }
	.notif-content { flex: 1; }
	.notif-title { font-size: 12px; font-weight: 600; color: var(--text-primary); }
	.notif-msg { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

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
