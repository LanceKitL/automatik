<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getAgentCommissions } from '$lib/services/api';
	import type { AgentCommissionItem } from '$lib/services/api';
import {
	ShoppingCart,
	DollarSign,
	Clock,
	CheckCircle,
	TrendingUp,
	Percent,
	Search,
	CircleDollarSign
} from '@lucide/svelte';

	let data = $state<AgentCommissionItem[]>([]);
	let loading = $state(true);
	let filterPaid = $state('all');
	let searchQuery = $state('');

	const now = new Date();
	const timestamp = now.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' })
		+ ' · ' + now.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' });

	const totalSales = $derived(data.length);
	const totalCommission = $derived(data.reduce((s, c) => s + Number(c.commission_amount), 0));
	const unpaidCount = $derived(data.filter(c => c.is_paid === 0).length);
	const paidCount = $derived(data.filter(c => c.is_paid === 1).length);
	const avgRate = $derived(
		data.length ? data.reduce((s, c) => s + Number(c.rate_applied), 0) / data.length : 0
	);
	const thisMonthCommission = $derived(
		data
			.filter(c => {
				const d = new Date(c.sale_date);
				const now = new Date();
				return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
			})
			.reduce((s, c) => s + Number(c.commission_amount), 0)
	);

	const displayData = $derived.by(() => {
		let list = data;
		if (filterPaid === 'paid') list = list.filter(c => c.is_paid === 1);
		if (filterPaid === 'unpaid') list = list.filter(c => c.is_paid === 0);
		if (searchQuery) {
			const q = searchQuery.toLowerCase();
			list = list.filter(c =>
				c.customer_name.toLowerCase().includes(q) ||
				c.brand.toLowerCase().includes(q) ||
				c.model.toLowerCase().includes(q)
			);
		}
		return list;
	});

	onMount(load);

	async function load() {
		loading = true;
		try {
			const res = await getAgentCommissions();
			data = res.data;
		} catch {
			toast.error('Failed to load sales.');
			data = [];
		} finally {
			loading = false;
		}
	}

	function formatCurrency(v: number): string {
		return '₱' + Number(v).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}

	function formatCompact(v: number): string {
		if (v >= 1_000_000) return '₱' + (v / 1_000_000).toFixed(1) + 'M';
		if (v >= 1_000) return '₱' + (v / 1_000).toFixed(0) + 'K';
		return '₱' + v.toFixed(0);
	}

	function formatDate(d: string): string {
		if (!d) return '—';
		const dt = new Date(d);
		return dt.toLocaleDateString('en-PH', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function saleStatusClass(s: string): string {
		const m: Record<string, string> = {
			pending: 's-pending',
			active: 's-progress',
			completed: 's-done',
			cancelled: 's-cancelled'
		};
		return m[s?.toLowerCase()] ?? 's-default';
	}

	function getVehicleColor(brand: string): string {
		const colors: Record<string, string> = {
			toyota: '#e53935',
			honda: '#1e88e5',
			nissan: '#c62828',
			mitsubishi: '#d32f2f',
			ford: '#1565c0',
			suzuki: '#2e7d32',
			hyundai: '#0288d1',
			bmw: '#1565c0',
			mercedes: '#424242',
			volkswagen: '#1565c0'
		};
		return colors[brand.toLowerCase()] ?? '#6b7280';
	}
</script>

<div class="page">

	<div class="top-bar">
		<div class="title-row">
			<h1>My Sales</h1>
			<p class="subtitle">Track your commissions and sales performance.</p>
		</div>
		<span class="timestamp">{timestamp}</span>
	</div>

	{#if loading}
		<div class="loading-state"><span class="spinner"></span><p>Loading sales data…</p></div>
	{:else}

		<!-- Stat cards -->
		<div class="stats-row">
			<div class="sc s1">
				<ShoppingCart size={20} />
				<div><span class="sc-val">{totalSales}</span><span class="sc-lbl">Total Sales</span></div>
			</div>
			<div class="sc s2">
				<DollarSign size={20} />
				<div><span class="sc-val">{formatCompact(totalCommission)}</span><span class="sc-lbl">Total Commission</span></div>
			</div>
			<div class="sc s3">
				<Clock size={20} />
				<div><span class="sc-val">{unpaidCount}</span><span class="sc-lbl">Pending</span></div>
			</div>
			<div class="sc s4">
				<CheckCircle size={20} />
				<div><span class="sc-val">{paidCount}</span><span class="sc-lbl">Paid</span></div>
			</div>
			<div class="sc s5">
				<Percent size={20} />
				<div><span class="sc-val">{avgRate.toFixed(2)}%</span><span class="sc-lbl">Avg Rate</span></div>
			</div>
			<div class="sc s6">
				<TrendingUp size={20} />
				<div><span class="sc-val">{formatCompact(thisMonthCommission)}</span><span class="sc-lbl">This Month</span></div>
			</div>
		</div>

		<!-- Toolbar -->
		<div class="toolbar">
			<div class="filter-group">
				<div class="pills">
					<button class="pill" class:active={filterPaid === 'all'} onclick={() => filterPaid = 'all'}>All</button>
					<button class="pill" class:active={filterPaid === 'paid'} onclick={() => filterPaid = 'paid'}>Paid</button>
					<button class="pill" class:active={filterPaid === 'unpaid'} onclick={() => filterPaid = 'unpaid'}>Unpaid</button>
				</div>
			</div>
			<div class="search-wrap">
				<Search size={14} />
				<input bind:value={searchQuery} placeholder="Search customer or vehicle…" />
			</div>
		</div>

		<!-- Table -->
		<div class="card">
			<table>
				<thead>
					<tr>
						<th>Sale</th>
						<th>Customer</th>
						<th>Vehicle</th>
						<th class="cell-right">Sale Price</th>
						<th class="cell-right">Rate</th>
						<th class="cell-right">Commission</th>
						<th>Paid</th>
						<th>Date</th>
						<th>Status</th>
					</tr>
				</thead>
				<tbody>
					{#each displayData as item (item.commission_id)}
						<tr>
							<td class="cell-mono">#{item.sale_id}</td>
							<td class="cell-name">{item.customer_name}</td>
							<td>
								<span class="vehicle-cell">
									<span class="v-icon" style="background:{getVehicleColor(item.brand)}">
										{item.brand.charAt(0)}
									</span>
									{item.brand} {item.model}
								</span>
							</td>
							<td class="cell-right cell-mono">{formatCurrency(item.selling_price)}</td>
							<td class="cell-right">
								<span class="rate-badge">
									{item.rate_applied}%
								</span>
							</td>
							<td class="cell-right cell-comm">{formatCurrency(item.commission_amount)}</td>
							<td>
								{#if item.is_paid}
									<span class="paid-badge paid" title={item.paid_at ? `Paid ${formatDate(item.paid_at)}` : ''}>
										<CheckCircle size={13} /> Paid
									</span>
								{:else}
									<span class="paid-badge unpaid" title="Awaiting payment">
										<Clock size={13} /> Pending
									</span>
								{/if}
							</td>
							<td class="cell-mono cell-date">{formatDate(item.sale_date)}</td>
							<td>
								<span class="sbadge {saleStatusClass(item.sale_status)}">
									<span class="sdot"></span>
									{item.sale_status}
								</span>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="9" class="empty-state">
								<CircleDollarSign size={28} />
								<p>No commissions yet. Sales you make will appear here.</p>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>

<style>
	.page { font-family: var(--font-sans); padding: 2rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; flex-direction: column; align-items: start; gap: 10px; }
	.subtitle { font-size: 14px; color: var(--text-muted); margin-top: 4px; }
	h1 { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
	.timestamp { font-family: var(--font-mono); font-size: 11px; color: var(--text-muted); background: var(--bg-muted); border: 0.5px solid var(--border); padding: 4px 12px; border-radius: 20px; }

	/* Loading */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }

	/* Stat cards */
	.stats-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 1.25rem; }
	.sc { background: var(--bg-stat); border-radius: 12px; padding: .9rem 1.1rem; display: flex; align-items: center; gap: 12px; position: relative; overflow: hidden; transition: transform .18s; }
	.sc:hover { transform: translateY(-2px); }
	.sc::before { content: ''; position: absolute; top: -10px; right: -10px; width: 56px; height: 56px; border-radius: 50%; opacity: .12; }
	.sc.s1::before { background: var(--accent); }
	.sc.s2::before { background: var(--primary-light); }
	.sc.s3::before { background: #fbbf24; }
	.sc.s4::before { background: var(--success); }
	.sc.s5::before { background: #a78bfa; }
	.sc.s6::before { background: #6de0b0; }
	.sc.s1 svg { color: var(--accent-dark); }
	.sc.s2 svg { color: var(--primary-dark); }
	.sc.s3 svg { color: #d97706; }
	.sc.s4 svg { color: var(--success-dark); }
	.sc.s5 svg { color: #7c3aed; }
	.sc.s6 svg { color: #059669; }
	.sc div { display: flex; flex-direction: column; }
	.sc-val { font-size: 26px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
	.sc-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; margin-top: 3px; }

	/* Toolbar */
	.toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-group { display: flex; align-items: center; gap: 6px; }
	.pills { display: flex; gap: 4px; flex-wrap: wrap; }
	.pill { font-size: 11px; padding: 5px 14px; border-radius: 20px; border: 0.5px solid var(--border); background: var(--bg-card); color: var(--text-light); cursor: pointer; transition: all .15s; font-weight: 500; }
	.pill:hover { background: var(--bg-hover); }
	.pill.active { background: var(--primary); color: var(--accent); border-color: var(--primary); }
	.search-wrap { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border-radius: 8px; border: 0.5px solid var(--border); background: var(--bg-card); }
	.search-wrap svg { color: var(--text-muted); flex-shrink: 0; }
	.search-wrap input { border: none; outline: none; background: transparent; font-size: 12px; color: var(--text-primary); min-width: 180px; }
	.search-wrap input::placeholder { color: var(--text-muted); }

	/* Card / Table */
	.card { background: var(--bg-card); border: 0.5px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; }
	table { width: 100%; border-collapse: collapse; }
	th { padding: 9px 1rem; text-align: left; font-size: 10px; font-weight: 600; color: var(--text-muted); letter-spacing: .6px; text-transform: uppercase; background: var(--bg-canvas); border-bottom: .5px solid var(--chart-grid); }
	td { padding: 10px 1rem; font-size: 12px; color: var(--text-light); border-top: .5px solid var(--border-lighter); vertical-align: middle; }
	tr:hover td { background: var(--bg-canvas); }
	.cell-right { text-align: right; }
	.cell-mono { font-family: var(--font-mono); font-size: 11px; }
	.cell-date { color: var(--text-muted); }
	.cell-name { font-weight: 600; color: var(--text-primary); }
	.cell-comm { font-weight: 700; color: var(--success-dark); font-size: 12px; }
	.empty-state { padding: 2.5rem; text-align: center; color: var(--text-muted); font-size: 13px; display: flex; flex-direction: column; align-items: center; gap: 8px; }
	.empty-state svg { opacity: .4; }

	/* Vehicle cell */
	.vehicle-cell { display: inline-flex; align-items: center; gap: 7px; }
	.v-icon { width: 22px; height: 22px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: 700; color: #fff; flex-shrink: 0; }

	/* Rate badge */
	.rate-badge { display: inline-block; padding: 2px 8px; border-radius: 6px; background: #fef3e2; color: #854f0b; font-size: 11px; font-weight: 700; font-family: var(--font-mono); }

	/* Paid badge */
	.paid-badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 600; white-space: nowrap; }
	.paid-badge.paid { background: var(--success-bg); color: var(--success-text); }
	.paid-badge.paid svg { color: var(--success-dark); }
	.paid-badge.unpaid { background: var(--warning-bg); color: var(--warning-text); }
	.paid-badge.unpaid svg { color: var(--warning-dark); }

	/* Sale status badge */
	.sbadge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-size: 10px; font-weight: 600; }
	.sdot { width: 5px; height: 5px; border-radius: 50%; }
	.s-pending { background: var(--warning-bg); color: var(--warning-text); }
	.s-pending .sdot { background: var(--warning-dark); }
	.s-progress { background: var(--info-bg); color: var(--info-text); }
	.s-progress .sdot { background: var(--info); }
	.s-done { background: var(--success-bg); color: var(--success-text); }
	.s-done .sdot { background: var(--success-dark); }
	.s-cancelled { background: var(--danger-bg); color: var(--danger-text); }
	.s-cancelled .sdot { background: var(--danger); }
	.s-default { background: var(--bg-hover); color: var(--text-light); }
	.s-default .sdot { background: #888; }

	@media (max-width: 900px) {
		.stats-row { grid-template-columns: repeat(3, 1fr); }
	}
	@media (max-width: 540px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.toolbar { flex-direction: column; align-items: stretch; }
		.search-wrap input { min-width: auto; width: 100%; }
	}
</style>
