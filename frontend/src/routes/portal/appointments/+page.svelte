<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { CalendarCheck, Clock, Car, User, X } from '@lucide/svelte';
	import { getCustomerServiceBookings, cancelServiceBooking } from '$lib/services/api';
	import type { ServiceBooking } from '$lib/services/api';

	let bookings = $state<ServiceBooking[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getCustomerServiceBookings();
			bookings = res.data.filter(b => b.booking_type === 'test_drive');
		} catch {
			toast.error('Failed to load appointments.');
			bookings = [];
		} finally {
			loading = false;
		}
	});

	async function cancelAppt(id: number) {
		try {
			await cancelServiceBooking(id);
			bookings = bookings.filter(b => b.booking_id !== id);
			toast.success('Appointment cancelled');
		} catch {
			toast.error('Failed to cancel appointment.');
		}
	}

	function formatDate(dt: string) {
		const d = new Date(dt);
		return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' });
	}

	function formatTime(dt: string) {
		const d = new Date(dt);
		return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', timeZone: 'UTC' });
	}

	let confirmed = $derived(bookings.filter(b => b.status !== 'cancelled'));
	let pending = $derived(bookings.filter(b => b.status === 'pending'));
</script>

<div class="page-header">
	<div>
		<h1>Test Drives</h1>
		<p class="subtitle">Your scheduled test drive appointments.</p>
	</div>
	<a href="/portal/vehicles" class="btn-primary">
		<CalendarCheck size={18} /> Browse Vehicles
	</a>
</div>

<div class="metrics">
	<div class="metric-card">
		<div class="metric-value">{confirmed.length}</div>
		<div class="metric-label">Total</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{confirmed.filter(b => b.status === 'confirmed' || b.status === 'completed').length}</div>
		<div class="metric-label">Confirmed</div>
	</div>
	<div class="metric-card">
		<div class="metric-value">{pending.length}</div>
		<div class="metric-label">Pending</div>
	</div>
</div>

{#if loading}
	<p class="loading">Loading appointments…</p>
{:else if bookings.length === 0}
	<div class="empty">No test drives yet. <a href="/portal/vehicles">Browse vehicles</a> to schedule one.</div>
{:else}
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>Date</th>
					<th>Time</th>
					<th>Type</th>
					<th>Vehicle</th>
					<th>Status</th>
					<th>Actions</th>
				</tr>
			</thead>
			<tbody>
				{#each bookings as b}
					<tr>
						<td><CalendarCheck size={14} class="icon-muted" /> {formatDate(b.slot_datetime)}</td>
						<td><Clock size={14} class="icon-muted" /> {formatTime(b.slot_datetime)}</td>
						<td><span class="type-tag" class:repair={b.booking_type === 'repair'} class:maintenance={b.booking_type === 'maintenance'} class:test_drive={b.booking_type === 'test_drive'}>{b.booking_type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span></td>
						<td><Car size={14} class="icon-muted" /> {b.brand} {b.model}</td>
						<td><span class="status-badge" class:confirmed={b.status === 'confirmed'} class:pending={b.status === 'pending'} class:cancelled={b.status === 'cancelled'} class:in_progress={b.status === 'in_progress'} class:completed={b.status === 'completed'}>{b.status.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}</span></td>
						<td>
							{#if b.status !== 'cancelled' && b.status !== 'completed'}
								<button class="btn-cancel" onclick={() => cancelAppt(b.booking_id)}><X size={14} /> Cancel</button>
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.page-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
	.btn-primary { display:inline-flex; align-items:center; gap:8px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-md); padding:10px 20px; font-size:14px; font-weight:600; cursor:pointer; text-decoration:none; }
	.btn-primary:hover { opacity:0.9; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:12px; margin-bottom:20px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; text-align:center; }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:12px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.loading, .empty { text-align:center; padding:40px 20px; color:var(--text-muted); }
	.empty a { color:var(--primary); }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); vertical-align:middle; }
	tr:last-child td { border-bottom:none; }
	.type-tag { display:inline-block; padding:2px 8px; border-radius:var(--radius-sm); font-size:11px; font-weight:600; }
	.type-tag.repair { background:#fef3c7; color:#92400e; }
	.type-tag.maintenance { background:#dbeafe; color:#1e40af; }
	.type-tag.test_drive { background:#d1fae5; color:#065f46; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.confirmed { background:#d1fae5; color:#065f46; }
	.status-badge.pending { background:#fef3c7; color:#92400e; }
	.status-badge.cancelled { background:#f3f4f6; color:#6b7280; }
	.status-badge.in_progress { background:#dbeafe; color:#1e40af; }
	.status-badge.completed { background:#d1fae5; color:#065f46; }
	.btn-cancel { background:#fef2f2; color:#dc2626; border:1px solid #fecaca; border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:4px; }
	.btn-cancel:hover { background:#fee2e2; }
</style>
