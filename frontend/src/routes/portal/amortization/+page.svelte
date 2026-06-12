<script lang="ts">
	import { onMount } from 'svelte';
	import { getMyAmortization } from '$lib/services/api';
	import { Calculator, CheckCircle2, Clock, AlertCircle } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let schedule = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getMyAmortization();
			schedule = res.data ?? [];
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});

	function statusClass(s: string) {
		if (s === 'paid' || s === 'completed') return 'status-paid';
		if (s === 'pending') return 'status-pending';
		if (s === 'overdue') return 'status-overdue';
		return 'status-pending';
	}

	function statusLabel(s: string) {
		if (s === 'paid' || s === 'completed') return 'Paid';
		if (s === 'pending') return 'Pending';
		if (s === 'overdue') return 'Overdue';
		return s.charAt(0).toUpperCase() + s.slice(1);
	}
</script>

<div class="page-header">
	<h1>Amortization Schedule</h1>
	<p class="subtitle">View your loan payment schedule and track payments.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if schedule.length === 0}
	<div class="empty">
		<Calculator size={48} />
		<p>No amortization schedule available.</p>
		<p class="empty-sub">Schedule appears once your loan is approved.</p>
	</div>
{:else}
	<div class="metrics">
		<div class="metric-card">
			<div class="metric-value">{schedule.length}</div>
			<div class="metric-label">Total Payments</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{schedule.filter(s => (s.status as string) === 'paid' || (s.status as string) === 'completed').length}</div>
			<div class="metric-label">Paid</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{schedule.filter(s => (s.status as string) === 'overdue').length}</div>
			<div class="metric-label">Overdue</div>
		</div>
	</div>

	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					<th>#</th>
					<th>Month</th>
					<th>Due Date</th>
					<th>Principal</th>
					<th>Interest</th>
					<th>Total Due</th>
					<th>Running Balance</th>
					<th>Status</th>
				</tr>
			</thead>
			<tbody>
				{#each schedule as row, i}
					<tr>
						<td>{row.month_number ?? i + 1}</td>
						<td>{row.month_number ?? i + 1}</td>
						<td>{row.due_date ? String(row.due_date).slice(0, 10) : '—'}</td>
						<td>₱{Number(row.principal ?? 0).toLocaleString()}</td>
						<td>₱{Number(row.interest ?? 0).toLocaleString()}</td>
						<td class="amount-cell">₱{Number(row.total_due ?? 0).toLocaleString()}</td>
						<td class="amount-cell">₱{Number(row.running_balance ?? 0).toLocaleString()}</td>
						<td>
							<span class="status-badge {statusClass(row.status as string)}">
								{statusLabel(row.status as string)}
							</span>
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
{/if}

<style>
	.page-header { margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:4px; }
	.loader { display:grid; place-items:center; height:50vh; }
	.empty { display:flex; flex-direction:column; align-items:center; gap:8px; padding:60px 20px; color:var(--text-muted); }
	.empty p { font-size:14px; margin:0; }
	.empty-sub { font-size:12px; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:14px; margin-bottom:24px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:18px 20px; text-align:center; box-shadow:var(--shadow-sm); }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); }
	tr:last-child td { border-bottom:none; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.status-badge.status-paid { background:#d1fae5; color:#065f46; }
	.status-badge.status-pending { background:#fef3c7; color:#92400e; }
	.status-badge.status-overdue { background:#fef2f2; color:#dc2626; }
</style>
