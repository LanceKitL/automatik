<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getCommissions, payCommission } from '$lib/services/api';
	import { toast } from 'svelte-sonner';
	import { Search, User, Clock, CheckCircle, X, Check } from '@lucide/svelte';

	interface CommissionItem {
		commission_id: number;
		sale_id: number;
		agent_id: number;
		rate_applied: number;
		commission_amount: number;
		is_paid: number;
		paid_at: string | null;
		customer_name: string;
		brand: string;
		model: string;
		year: number;
		agent_name: string;
	}

	let loading = $state(true);
	let error = $state<string | null>(null);
	let commissions = $state<CommissionItem[]>([]);

	let searchQuery = $state('');
	let activeFilter = $state<'all' | 'unpaid' | 'paid'>('all');

	let showConfirm = $state(false);
	let confirmId = $state<number | null>(null);

	const tableColumns = [
		{ key: 'id', label: 'ID' },
		{ key: 'agent', label: 'Agent' },
		{ key: 'sale_id', label: 'Sale ID' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'amount', label: 'Amount' },
		{ key: 'rate', label: 'Rate' },
		{ key: 'status', label: 'Status' },
		{ key: 'paid_at', label: 'Paid At' },
		{ key: 'actions', label: 'Actions' }
	];

	const filters = ['all', 'unpaid', 'paid'] as const;


	let stats = $derived({
		total: commissions.length,
		unpaid: commissions.filter((c) => Number(c.is_paid) !== 1).length,
		paid: commissions.filter((c) => Number(c.is_paid) === 1).length
	});

	let filteredCommissions = $derived.by(() => {
		let list = commissions;
		if (activeFilter === 'paid') {
			list = list.filter((c) => c.is_paid == 1);
		} else if (activeFilter === 'unpaid') {
			list = list.filter((c) => c.is_paid != 1);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(c) =>
					String(c.agent_name ?? '').toLowerCase().includes(q) ||
					String(c.customer_name ?? '').toLowerCase().includes(q) ||
					String(c.sale_id).includes(q) ||
					String(c.commission_amount).includes(q)
			);
		}
		return list;
	});

	function formatAmount(n: number): string {
		return '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
	}

	function formatDate(d: string | null): string {
		if (!d) return '—';
		return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function promptPay(id: number) {
		confirmId = id;
		showConfirm = true;
	}

	function cancelPay() {
		showConfirm = false;
		confirmId = null;
	}

	async function confirmPay() {
		if (confirmId === null) return;
		try {
			await payCommission(confirmId);
			toast.success(`Commission #${confirmId} marked as paid.`);
			showConfirm = false;
			confirmId = null;
			await loadCommissions();
		} catch (e) {
			toast.error((e as Error).message || 'Failed to pay commission.');
			showConfirm = false;
			confirmId = null;
		}
	}

	async function loadCommissions() {
		loading = true;
		error = null;
		try {
			const res = await getCommissions();
			
			commissions = (Array.isArray(res) ? res : []).map(c => ({
				...c,
				is_paid: Number(c.is_paid)
			})) as CommissionItem[];
		} catch (e) {
			toast.error((e as Error).message || 'Failed to load commissions.');
			error = null;
		} finally {
			loading = false;
		}
	}

	onMount(loadCommissions);
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Commissions</h1>
				<p class="title-subtitle">Manage agent commission payouts</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by agent, sale ID…"
					bind:value={searchQuery}
				/>
			</div>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-all">
			<User size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-unpaid">
			<Clock size={18} />
			<div>
				<span class="mini-val">{stats.unpaid}</span>
				<span class="mini-lbl">Unpaid</span>
			</div>
		</div>
		<div class="mini-stat s-paid">
			<CheckCircle size={18} />
			<div>
				<span class="mini-val">{stats.paid}</span>
				<span class="mini-lbl">Paid</span>
			</div>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each filters as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading commissions…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredCommissions.length === 0}
		<div class="empty-state">No commissions found.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredCommissions as c (c.commission_id)}
				<tr>
					<td><span class="cell-id">#{c.commission_id}</span></td>
					<td class="cell-agent">{c.agent_name ?? 'Agent #' + c.agent_id}</td>
					<td><span class="cell-sale-id">#{c.sale_id}</span></td>
					<td class="cell-customer">{c.customer_name ?? '—'}</td>
					<td><span class="cell-amount">{formatAmount(c.commission_amount)}</span></td>
					<td><span class="cell-rate">{c.rate_applied}%</span></td>
					<td>
						<span class="badge badge-{c.is_paid == 1 ? 'paid' : 'unpaid'}">
							{c.is_paid == 1 ? 'Paid' : 'Unpaid'}
						</span>
					</td>
					<td class="cell-date">{formatDate(c.paid_at)}</td>
					<td>
						{#if Number(c.is_paid) !== 1}
							<button class="action-btn" onclick={() => promptPay(c.commission_id)}>
								Mark as Paid
							</button>
						{/if}
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- Confirm modal -->
{#if showConfirm}
	<div class="modal-overlay" onclick={cancelPay} onkeydown={(e) => { if (e.key === 'Escape') cancelPay(); }} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} onkeydown={(e) => { if (e.key === 'Escape') cancelPay(); }} role="dialog" tabindex="-1">
			<div class="modal-header">
				<h2>Confirm Payment</h2>
				<button class="modal-close" onclick={cancelPay}><X size={16} /></button>
			</div>
			<div class="modal-body">
				<p>Mark commission <strong>#{confirmId}</strong> as paid?</p>
			</div>
			<div class="modal-footer">
				<button class="btn btn-cancel" onclick={cancelPay}>No</button>
				<button class="btn btn-confirm" onclick={confirmPay}>Yes</button>
			</div>
		</div>
	</div>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-all :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-unpaid :global(svg) { color: #b45309; flex-shrink: 0; }
	.s-paid :global(svg) { color: #059669; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 14px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-agent { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.cell-sale-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #6b7280; }
	.cell-customer { font-size: 12px; color: #1a1a2e; font-weight: 500; }
	.cell-amount { font-family: 'DM Mono', monospace; font-size: 12px; color: #059669; font-weight: 500; }
	.cell-rate { font-family: 'DM Mono', monospace; font-size: 11px; color: #6b7280; }
	.cell-date { font-size: 12px; color: #6b7280; }

	/* Status badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-paid { background: #ecfdf5; color: #059669; }
	.badge-unpaid { background: #fef3c7; color: #b45309; }

	/* Action button */
	.action-btn { height: 26px; padding: 0 10px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 6px; font-family: 'Syne', sans-serif; font-size: 10px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; white-space: nowrap; }
	.action-btn:hover { opacity: 0.85; }
	.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }

	/* Modal */
	.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.45); display: flex; align-items: center; justify-content: center; z-index: 1000; }
	.modal { background: #fff; border-radius: 12px; width: 380px; max-width: 90vw; box-shadow: 0 20px 60px rgba(0,0,0,.15); font-family: 'Syne', sans-serif; }
	.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.25rem; border-bottom: 0.5px solid #e5e7eb; }
	.modal-header h2 { font-size: 15px; font-weight: 700; color: #1a1a2e; margin: 0; }
	.modal-close { background: none; border: none; cursor: pointer; color: #9ca3af; padding: 4px; border-radius: 6px; display: flex; transition: .1s; }
	.modal-close:hover { background: #f3f4f6; color: #1a1a2e; }
	.modal-body { padding: 1.25rem; font-size: 13px; color: #374151; }
	.modal-body p { margin: 0; }
	.modal-footer { display: flex; gap: 8px; justify-content: flex-end; padding: 1rem 1.25rem; border-top: 0.5px solid #e5e7eb; }
	.btn { height: 34px; padding: 0 18px; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; border: none; transition: opacity .15s; }
	.btn-cancel { background: #f3f4f6; color: #374151; }
	.btn-cancel:hover { opacity: 0.8; }
	.btn-confirm { background: #1a1a2e; color: #e8c97e; }
	.btn-confirm:hover { opacity: 0.85; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
