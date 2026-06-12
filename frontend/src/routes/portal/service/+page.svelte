<script lang="ts">
	import { onMount } from 'svelte';
	import { Wrench, Calendar, Car, Clock, X } from '@lucide/svelte';

	let bookings = $state([
		{ id: 1, dateTime: 'Jun 10, 2026 - 10:00 AM', type: 'Repair', vehicle: 'Toyota Fortuner', warranty: 'WC-2024-00471', status: 'Confirmed' },
		{ id: 2, dateTime: 'Jun 14, 2026 - 09:00 AM', type: 'Maintenance', vehicle: 'Honda Civic', warranty: '—', status: 'Pending' },
	]);
	let loading = $state(false);
	let filter = $state('all');
	let showModal = $state(false);

	const types = ['all', 'repair', 'maintenance', 'test-drive'];

	let filtered = $derived(
		filter === 'all' ? bookings : bookings.filter(b => b.type.toLowerCase().replace(' ', '-') === filter)
	);

	function removeBooking(id: number) {
		bookings = bookings.filter(b => b.id !== id);
	}
</script>

<div class="page-header">
	<div>
		<h1>Service Bookings</h1>
		<p class="subtitle">Manage your appointments — repairs, maintenance, and test drives.</p>
	</div>
	<button class="btn-primary" onclick={showModal = true}>
		<Wrench size={18} /> Book a Service
	</button>
</div>

<div class="metrics">
	<div class="metric-card">
		<div class="metric-value">{bookings.length}</div>
		<div class="metric-label">Total Bookings</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{bookings.filter(b => b.status === 'Pending').length}</div>
		<div class="metric-label">Pending</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{bookings.filter(b => b.status === 'Confirmed').length}</div>
		<div class="metric-label">Confirmed</div>
	</div>
</div>

<div class="filters">
	{#each types as t}
		<button class="filter-tab" class:active={filter === t} onclick={() => filter = t}>
			{t === 'all' ? 'All' : t.charAt(0).toUpperCase() + t.slice(1).replace('-', ' ')}
		</button>
	{/each}
</div>

{#if loading}
	<p class="loading">Loading bookings…</p>
{:else if filtered.length === 0}
	<div class="empty">No bookings found. Click "Book a Service" to get started.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Date & Time</th>
					<th>Type</th>
					<th>Vehicle</th>
					<th>Warranty</th>
					<th>Status</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each filtered as b}
					<tr>
						<td><Calendar size={14} class="icon-muted" /> {b.dateTime}</td>
						<td><span class="type-tag" class:repair={b.type === 'Repair'} class:maintenance={b.type === 'Maintenance'} class:test-drive={b.type === 'Test drive'}>{b.type}</span></td>
						<td><Car size={14} class="icon-muted" /> {b.vehicle}</td>
						<td>{b.warranty}</td>
						<td><span class="status-badge" class:confirmed={b.status === 'Confirmed'} class:pending={b.status === 'Pending'}>{b.status}</span></td>
						<td><button class="btn-cancel" onclick={() => removeBooking(b.id)}><X size={14} /> Cancel</button></td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<!-- Modal placeholder - full booking flow would be built out later -->
{#if showModal}
	<div class="modal-overlay" onclick={() => showModal = false}>
		<div class="modal" onclick={(e) => e.stopPropagation()}>
			<div class="modal-header">
				<h2>Book a Service</h2>
				<button class="modal-close" onclick={() => showModal = false}><X size={20} /></button>
			</div>
			<div class="modal-body">
				<p style="color:var(--text-muted);font-size:14px;">Service booking flow coming soon. Select from repair, maintenance, or test drive.</p>
			</div>
			<div class="modal-footer">
				<button class="btn-secondary" onclick={() => showModal = false}>Cancel</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.page-header {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		margin-bottom: 24px;
	}
	h1 {
		font-size: 24px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0;
	}
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		background: var(--primary);
		color: var(--text-white);
		border: none;
		border-radius: var(--radius-md);
		padding: 10px 20px;
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
	}
	.btn-primary:hover {
		opacity: 0.9;
	}
	.metrics {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
		gap: 12px;
		margin-bottom: 20px;
	}
	.metric-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		padding: 16px 20px;
		text-align: center;
	}
	.metric-value {
		font-size: 28px;
		font-weight: 700;
		color: var(--primary);
	}
	.metric-label {
		font-size: 12px;
		color: var(--text-muted);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-top: 4px;
	}
	.filters {
		display: flex;
		gap: 6px;
		margin-bottom: 16px;
	}
	.filter-tab {
		padding: 6px 14px;
		border: 1px solid var(--border);
		border-radius: 20px;
		background: var(--bg-card);
		font-size: 12px;
		color: var(--text-dark);
		cursor: pointer;
		font-family: inherit;
		font-weight: 500;
	}
	.filter-tab.active {
		background: var(--primary);
		color: var(--text-white);
		border-color: var(--primary);
	}
	.loading, .empty {
		text-align: center;
		padding: 40px 20px;
		color: var(--text-muted);
	}
	.table-wrapper {
		overflow-x: auto;
		background: var(--bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--border);
		box-shadow: var(--shadow-sm);
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}
	th {
		text-align: left;
		padding: 0.75rem 1rem;
		color: var(--text-muted);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		border-bottom: 1px solid var(--border);
		background: var(--bg-muted);
	}
	td {
		padding: 0.65rem 1rem;
		border-bottom: 1px solid var(--border-lighter);
		color: var(--text-primary);
		vertical-align: middle;
	}
	tr:last-child td {
		border-bottom: none;
	}
	.icon-muted {
		color: var(--text-muted);
		display: inline;
		margin-right: 4px;
		vertical-align: middle;
	}
	.type-tag {
		display: inline-block;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: 11px;
		font-weight: 600;
	}
	.type-tag.repair { background: #fef3c7; color: #92400e; }
	.type-tag.maintenance { background: #dbeafe; color: #1e40af; }
	.type-tag.test-drive { background: #d1fae5; color: #065f46; }
	.status-badge {
		display: inline-block;
		padding: 2px 10px;
		border-radius: 20px;
		font-size: 11px;
		font-weight: 600;
	}
	.status-badge.confirmed { background: #d1fae5; color: #065f46; }
	.status-badge.pending { background: #fef3c7; color: #92400e; }
	.btn-cancel {
		background: #fef2f2;
		color: #dc2626;
		border: 1px solid #fecaca;
		border-radius: var(--radius-sm);
		padding: 4px 10px;
		font-size: 11px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		display: inline-flex;
		align-items: center;
		gap: 4px;
	}
	.btn-cancel:hover {
		background: #fee2e2;
	}
	.modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.4);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}
	.modal {
		background: var(--bg-card);
		border-radius: var(--radius-lg);
		width: 500px;
		max-width: 90vw;
		box-shadow: var(--shadow-lg);
	}
	.modal-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 24px;
		border-bottom: 1px solid var(--border);
	}
	.modal-header h2 {
		font-size: 18px;
		font-weight: 700;
		margin: 0;
	}
	.modal-close {
		background: none;
		border: none;
		cursor: pointer;
		color: var(--text-muted);
		padding: 4px;
		border-radius: var(--radius-sm);
	}
	.modal-close:hover {
		background: var(--bg-hover);
	}
	.modal-body {
		padding: 20px 24px;
	}
	.modal-footer {
		padding: 16px 24px;
		border-top: 1px solid var(--border);
		display: flex;
		justify-content: flex-end;
		gap: 8px;
	}
	.btn-secondary {
		padding: 8px 16px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		color: var(--text-dark);
		font-size: 14px;
		font-weight: 500;
		cursor: pointer;
		font-family: inherit;
	}
</style>
