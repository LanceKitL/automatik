<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { getFinanceInsurance } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { Shield, Plus, Search } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';
	import CreateInsuranceDrawer from './CreateInsuranceDrawer.svelte';

	let records = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let search = $state('');
	let showDrawer = $state(false);

	onMount(async () => {
		try {
			const res = await getFinanceInsurance();
			records = res.data ?? [];
		} catch {
			toast.error('Failed to load insurance records.');
		} finally {
			loading = false;
		}
	});

	let filtered = $derived(
		search
			? records.filter(r =>
				String(r.policy_number ?? '').toLowerCase().includes(search.toLowerCase()) ||
				String(r.provider_name ?? '').toLowerCase().includes(search.toLowerCase()) ||
				String(r.customer_name ?? '').toLowerCase().includes(search.toLowerCase())
			  )
			: records
	);

	function statusClass(s: string) {
		if (s === 'active') return 'badge-active';
		if (s === 'expired') return 'badge-expired';
		if (s === 'cancelled') return 'badge-cancelled';
		return '';
	}
</script>

<div class="page">
	<div class="page-header">
		<div>
			<h1>Insurance</h1>
			<p class="subtitle">Manage insurance policies linked to sales.</p>
		</div>
		<button class="btn-primary" onclick={() => showDrawer = true}>
			<Plus size={18} /> Add Insurance
		</button>
	</div>

	<div class="metrics">
		<div class="metric-card">
			<div class="metric-value">{records.length}</div>
			<div class="metric-label">Total Policies</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{records.filter(r => r.status === 'active').length}</div>
			<div class="metric-label">Active</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{records.filter(r => r.status === 'expired').length}</div>
			<div class="metric-label">Expired</div>
		</div>
		<div class="metric-card">
			<div class="metric-value">{records.filter(r => r.status === 'cancelled').length}</div>
			<div class="metric-label">Cancelled</div>
		</div>
	</div>

	<div class="search-bar">
		<Search size={16} />
		<input type="text" placeholder="Search by policy #, provider, or customer..." bind:value={search} />
	</div>

	{#if loading}
		<div class="loader"><Loader /></div>
	{:else if filtered.length === 0}
		<div class="empty">No insurance records found.</div>
	{:else}
		<div class="table-wrapper">
			<table>
				<thead>
					<tr>
						<th>Policy #</th>
						<th>Provider</th>
						<th>Customer</th>
						<th>Vehicle</th>
						<th>Coverage</th>
						<th>Start</th>
						<th>End</th>
						<th>Status</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each filtered as r (r.insurance_id)}
						<tr>
							<td class="policy-no">{r.policy_number as string}</td>
							<td>{r.provider_name as string}</td>
							<td>{r.customer_name as string}</td>
							<td>{(r.brand as string) ?? ''} {(r.model as string) ?? ''}</td>
							<td>{r.coverage_type as string ?? '—'}</td>
							<td>{r.start_date ? String(r.start_date).slice(0, 10) : '—'}</td>
							<td>{r.end_date ? String(r.end_date).slice(0, 10) : '—'}</td>
							<td><span class="status-badge {statusClass(r.status as string)}">{(r.status as string) ?? '—'}</span></td>
							<td>
								<button class="btn-view" onclick={() => goto(`/finance_staff/insurance/${r.insurance_id}`)}>View</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

{#if showDrawer}
	<CreateInsuranceDrawer onclose={() => { showDrawer = false; }} />
{/if}

<style>
	.page { font-family: var(--font-sans); padding: 2rem 1.5rem; }
	.page-header { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:24px; }
	h1 { font-size:24px; font-weight:700; color:var(--text-dark); margin:0; }
	.subtitle { font-size:14px; color:var(--text-muted); margin-top:9px; }
	.btn-primary { display:inline-flex; align-items:center; gap:8px; background:var(--primary); color:var(--text-white); border:none; border-radius:var(--radius-md); padding:10px 20px; font-size:14px; font-weight:600; cursor:pointer; }
	.btn-primary:hover { opacity:0.9; }
	.metrics { display:grid; grid-template-columns:repeat(auto-fit, minmax(120px, 1fr)); gap:12px; margin-bottom:20px; }
	.metric-card { background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); padding:16px; text-align:center; }
	.metric-value { font-size:28px; font-weight:700; color:var(--primary); }
	.metric-label { font-size:11px; color:var(--text-muted); font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-top:4px; }
	.search-bar { display:flex; align-items:center; gap:8px; padding:8px 14px; background:var(--bg-card); border:1px solid var(--border); border-radius:var(--radius-md); margin-bottom:16px; color:var(--text-muted); }
	.search-bar input { flex:1; border:none; background:none; outline:none; font-size:13px; color:var(--text-dark); }
	.loader { display:grid; place-items:center; height:30vh; }
	.empty { text-align:center; padding:40px; color:var(--text-muted); }
	.table-wrapper { overflow-x:auto; background:var(--bg-card); border-radius:var(--radius-md); border:1px solid var(--border); box-shadow:var(--shadow-sm); }
	table { width:100%; border-collapse:collapse; font-size:0.85rem; }
	th { text-align:left; padding:0.75rem 1rem; color:var(--text-muted); font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em; border-bottom:1px solid var(--border); background:var(--bg-muted); }
	td { padding:0.65rem 1rem; border-bottom:1px solid var(--border-lighter); color:var(--text-primary); vertical-align:middle; }
	tr:last-child td { border-bottom:none; }
	.policy-no { font-family:monospace; font-weight:600; }
	.status-badge { display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }
	.badge-active { background:#d1fae5; color:#065f46; }
	.badge-expired { background:#fef3c7; color:#92400e; }
	.badge-cancelled { background:#fef2f2; color:#dc2626; }
	.btn-view { background:var(--primary-bg); color:var(--primary); border:1px solid var(--primary); border-radius:var(--radius-sm); padding:4px 10px; font-size:11px; font-weight:600; cursor:pointer; }
	.btn-view:hover { background:var(--primary); color:var(--text-white); }
</style>
