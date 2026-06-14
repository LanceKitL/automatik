<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getServiceStaffDashboard } from '$lib/services/api';
	import type { ServiceStaffDashboardResponse } from '$lib/services/api';
	import { formatDateShort } from '$lib/utils/format';

	let data = $state<ServiceStaffDashboardResponse['data'] | null>(null);
	let loading = $state(true);
	let animatedRepair = $state(0);
	let animatedMaintenance = $state(0);
	let animatedWarranty = $state(0);
	let animatedResolved = $state(0);
	let animatedRevenue = $state(0);
	let maintTab = $state('all');

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

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

	function statusClass(status: string | null | undefined): string {
		if (!status) return 's-default';
		const s = status.toLowerCase();
		if (s === 'confirmed' || s === 'approved' || s === 'resolved') return 's-confirmed';
		if (s === 'pending' || s === 'submitted') return 's-pending';
		if (s === 'cancelled' || s === 'rejected') return 's-cancelled';
		if (s === 'under_review' || s === 'draft_estimate') return 's-review';
		if (s === 'in_progress' || s === 'awaiting_signature') return 's-progress';
		if (s === 'completed') return 's-completed';
		return 's-default';
	}

	onMount(async () => {
		try {
			const res = await getServiceStaffDashboard();
			data = res.data;
			animateValue(v => animatedRepair = v, data.for_repair);
			animateValue(v => animatedMaintenance = v, data.for_maintenance);
			animateValue(v => animatedWarranty = v, data.warranty_claims);
			animateValue(v => animatedResolved = v, data.resolved_services);
			animateValue(v => animatedRevenue = v, data.accumulated_revenue);
		} catch (e) {
			console.error('Failed to load dashboard:', e);
			toast.error('Failed to load dashboard.');
		} finally {
			loading = false;
		}
	});

	function filteredMaint() {
		if (!data) return [];
		if (maintTab === 'ongoing') return data.maintenance_list.filter((b: any) => ['pending', 'confirmed', 'in_progress'].includes((b as any).status));
		if (maintTab === 'under_review') return data.maintenance_list.filter((b: any) => ['draft_estimate', 'awaiting_signature'].includes((b as any).status));
		if (maintTab === 'resolved') return data.maintenance_list.filter((b: any) => (b as any).status === 'completed');
		return data.maintenance_list;
	}

	let maintTabFiltered = $derived(filteredMaint());

	function badgeClass(bt: string | null): string {
		if (bt === 'repair') return 'badge-blue';
		if (bt === 'maintenance') return 'badge-green';
		if (bt === 'warranty') return 'badge-orange';
		return 'badge-gray';
	}
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
				<h1>Service Staff Dashboard</h1>
				<p class="subtitle">Hi there, ready to fix vehicles?</p>
			</div>
			<span class="timestamp">{timestamp}</span>
		</div>

		<!-- Stat Cards -->
		<div class="cards">
			<div class="stat-card c1">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
				</div>
				<div class="stat-value">{animatedRepair.toLocaleString()}</div>
				<div class="stat-label">For Repair</div>
			</div>
			<div class="stat-card c2">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
				</div>
				<div class="stat-value">{animatedMaintenance.toLocaleString()}</div>
				<div class="stat-label">For Maintenance</div>
			</div>
			<div class="stat-card c3">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
				</div>
				<div class="stat-value">{animatedWarranty.toLocaleString()}</div>
				<div class="stat-label">Warranty Claims</div>
			</div>
			<div class="stat-card c4">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
				</div>
				<div class="stat-value">{animatedResolved.toLocaleString()}</div>
				<div class="stat-label">Resolved Services</div>
			</div>
			<div class="stat-card c5">
				<div class="stat-icon">
					<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
				</div>
				<div class="stat-value">₱{Math.round(animatedRevenue).toLocaleString()}</div>
				<div class="stat-label">Accumulated Revenue</div>
			</div>
		</div>

		<!-- Sections -->
		<div class="sections">

			<!-- Maintenance -->
			<div class="section-card">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
						Maintenance
					</span>
					<span class="count-pill">{data.maintenance_list.length}</span>
				</div>
				<div class="tab-bar">
					<button class:active={maintTab === 'all'} onclick={() => maintTab = 'all'}>All</button>
					<button class:active={maintTab === 'ongoing'} onclick={() => maintTab = 'ongoing'}>Ongoing</button>
					<button class:active={maintTab === 'under_review'} onclick={() => maintTab = 'under_review'}>Under Review</button>
					<button class:active={maintTab === 'resolved'} onclick={() => maintTab = 'resolved'}>Resolved</button>
				</div>
				{#if maintTabFiltered.length > 0}
					<table class="data-table">
						<thead>
							<tr><th>ID</th><th>Customer</th><th>Vehicle</th><th>Status</th><th>Date</th></tr>
						</thead>
						<tbody>
							{#each maintTabFiltered as entry}
								{@const b = entry as any}
								<tr>
									<td class="id-cell">{b.booking_id}</td>
									<td>{b.customer_name ?? '—'}</td>
									<td>{b.brand ?? ''} {b.model ?? ''} ({b.year ?? ''})</td>
									<td><span class="status-badge {statusClass(b.status)}">{b.status ?? '—'}</span></td>
									<td>{formatDateShort(b.slot_datetime)}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<div class="empty-state">No maintenance records.</div>
				{/if}
			</div>

			<!-- Warranty Claims -->
			<div class="section-card">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
						Warranty Claims
					</span>
					<span class="count-pill">{data.warranty_claims_list.length}</span>
				</div>
				{#if data.warranty_claims_list.length > 0}
					<table class="data-table">
						<thead>
							<tr><th>ID</th><th>Customer</th><th>Vehicle</th><th>Type</th><th>Status</th><th>Date</th></tr>
						</thead>
						<tbody>
							{#each data.warranty_claims_list as claim}
								{@const w = claim as any}
								<tr>
									<td class="id-cell">{w.claim_id}</td>
									<td>{w.customer_name ?? '—'}</td>
									<td>{w.brand ?? ''} {w.model ?? ''}</td>
									<td><span class={badgeClass(w.claim_type)}>{w.claim_type ?? '—'}</span></td>
									<td><span class="status-badge {statusClass(w.status)}">{w.status ?? '—'}</span></td>
									<td>{w.submitted_at ? String(w.submitted_at).slice(0, 10) : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<div class="empty-state">No warranty claims.</div>
				{/if}
			</div>

			<!-- History -->
			<div class="section-card full-width">
				<div class="section-head">
					<span class="section-title">
						<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
						History
					</span>
					<span class="count-pill">{data.history.length}</span>
				</div>
				{#if data.history.length > 0}
					<table class="data-table">
						<thead>
							<tr><th>ID</th><th>Customer</th><th>Vehicle</th><th>Type</th><th>Status</th><th>Date</th></tr>
						</thead>
						<tbody>
							{#each data.history as hitem}
								{@const h = hitem as any}
								<tr>
									<td class="id-cell">{h.booking_id ?? h.claim_id}</td>
									<td>{h.customer_name ?? '—'}</td>
									<td>{h.brand ?? ''} {h.model ?? ''}</td>
									<td><span class={badgeClass(h.entry_type)}>{h.entry_type ?? '—'}</span></td>
									<td><span class="status-badge {statusClass(h.status)}">{h.status ?? '—'}</span></td>
									<td>{h.slot_datetime ? formatDateShort(h.slot_datetime) : h.resolved_at ? formatDateShort(h.resolved_at) : '—'}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{:else}
					<div class="empty-state">No history records.</div>
				{/if}
			</div>

		</div>
	</div>
{:else}
	<div class="error-state">
		<p>Failed to load dashboard data. Please try again later.</p>
		<button class="retry-btn" onclick={() => window.location.reload()}>Retry</button>
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
	.logo-row { display: flex; flex-direction: column; align-items: start; justify-content: start; }
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	h1 {
		font-size: 24px;
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
	.stat-card.c1::before { background: #f0c27a; }
	.stat-card.c2::before { background: #6de0b0; }
	.stat-card.c3::before { background: #f77c7c; }
	.stat-card.c4::before { background: #7ed6df; }
	.stat-card.c5::before { background: var(--accent); }
	.stat-icon {
		margin-bottom: 10px;
		display: flex;
	}
	.stat-card.c1 .stat-icon { color: #d4a040; }
	.stat-card.c2 .stat-icon { color: var(--success); }
	.stat-card.c3 .stat-icon { color: var(--danger); }
	.stat-card.c4 .stat-icon { color: #3498db; }
	.stat-card.c5 .stat-icon { color: var(--accent-dark); }
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

	/* ---------- Tab Bar ---------- */
	.tab-bar {
		display: flex;
		gap: 0;
		border-bottom: 0.5px solid var(--border-lighter);
		background: var(--bg-canvas);
		padding: 0 1.25rem;
	}
	.tab-bar button {
		padding: 0.5rem 0.75rem;
		font-size: 11px;
		font-weight: 500;
		color: var(--text-muted);
		background: none;
		border: none;
		border-bottom: 2px solid transparent;
		cursor: pointer;
		transition: color 0.15s, border-color 0.15s;
	}
	.tab-bar button.active {
		color: var(--primary);
		border-bottom-color: var(--primary);
	}
	.tab-bar button:hover:not(.active) {
		color: var(--text-primary);
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
	.s-review     { background: rgba(124,157,247,0.18); color: var(--primary-dark); }
	.s-progress   { background: rgba(124,157,247,0.12); color: #5b6abf; }
	.s-completed  { background: rgba(109,224,176,0.18); color: var(--success); }
	.s-default    { background: var(--bg-hover); color: var(--text-light); }

	.badge-blue   { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; background: rgba(124,157,247,0.18); color: var(--primary-dark); }
	.badge-green  { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; background: rgba(109,224,176,0.18); color: var(--success); }
	.badge-orange { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; background: rgba(247,199,117,0.18); color: #b8860b; }
	.badge-gray   { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: 600; background: var(--bg-hover); color: var(--text-light); }

	/* ---------- Empty State ---------- */
	.empty-state {
		padding: 2rem 1.25rem;
		text-align: center;
		color: var(--text-muted);
		font-size: 12px;
	}

	/* ---------- Error State ---------- */
	.error-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 40vh;
		gap: 1rem;
		color: var(--text-light);
		font-family: var(--font-sans);
		text-align: center;
	}
	.retry-btn {
		padding: 0.5rem 1.5rem;
		font-size: 13px;
		font-weight: 500;
		color: var(--text-white);
		background: var(--primary);
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
	}
	.retry-btn:hover {
		opacity: 0.9;
	}

	/* ---------- Responsive ---------- */
	@media (max-width: 720px) {
		.sections { grid-template-columns: 1fr; }
		.cards { grid-template-columns: repeat(2, 1fr); }
		.top-bar { flex-wrap: wrap; gap: 8px; }
	}
</style>
