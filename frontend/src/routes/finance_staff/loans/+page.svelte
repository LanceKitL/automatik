<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		getFinanceLoans,
		type LoanItem
	} from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { Banknote, Search, Plus } from '@lucide/svelte';
	import CreateLoanDrawer from './CreateLoanDrawer.svelte';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let loans = $state<LoanItem[]>([]);

	// ── Drawer ────────────────────────────────────────────────────────────────
	let showCreateDrawer = $state(false);

	function handleDrawerClose() {
		showCreateDrawer = false;
		loadLoans();
	}

	function resetForm() {
		// no-op on drawer close handled by handleDrawerClose
	}

	// ── Tabs (from URL ?tab=) ────────────────────────────────────────────────
	let activeTab = $derived(($page.url.searchParams.get('tab') ?? 'all').toLowerCase());

	const TABS = [
		{ key: 'all', label: 'All' },
		{ key: 'pending', label: 'Pending' },
		{ key: 'approved', label: 'Approved' },
		{ key: 'rejected', label: 'Rejected' }
	] as const;

	function switchTab(tab: string) {
		goto(`/finance_staff/loans?tab=${tab}`, { replaceState: true });
	}

	// ── Search ───────────────────────────────────────────────────────────────
	let searchQuery = $state('');

	// ── Stats ─────────────────────────────────────────────────────────────────
	let stats = $derived.by(() => {
		const pending = loans.filter((l) => l.bank_approval_status === 'pending').length;
		const approved = loans.filter((l) => l.bank_approval_status === 'approved').length;
		const rejected = loans.filter((l) => l.bank_approval_status === 'rejected').length;
		return { total: loans.length, pending, approved, rejected };
	});

	let filteredLoans = $derived.by(() => {
		let list = loans;
		if (activeTab !== 'all') {
			list = list.filter((l) => l.bank_approval_status === activeTab);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(l) =>
					String(l.loan_id).includes(q) ||
					String(l.sale_id).includes(q) ||
					l.customer_name.toLowerCase().includes(q) ||
					l.brand.toLowerCase().includes(q) ||
					l.model.toLowerCase().includes(q)
			);
		}
		return list;
	});

	const tableColumns = [
		{ key: 'id', label: 'Loan #' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'amount', label: 'Amount' },
		{ key: 'down', label: 'Down Pay' },
		{ key: 'rate', label: 'Rate' },
		{ key: 'term', label: 'Term' },
		{ key: 'monthly', label: 'Monthly' },
		{ key: 'bank', label: 'Bank' },
		{ key: 'status', label: 'Status' },
		{ key: 'actions', label: 'Actions' }
	];

	async function loadLoans() {
		loading = true;
		error = null;
		try {
			const res = await getFinanceLoans();
			loans = res.data ?? [];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadLoans);

	function fmt(n: string | number | null | undefined): string {
		if (n == null) return '—';
		return `₱${Number(n).toLocaleString()}`;
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<h1>Loans & Amortization</h1>
			<span style="color:var(--text-muted); margin-top:4px; font-size:14px">Click <code>view</code> to see the amortization schedule</span>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by ID, customer, vehicle…"
					bind:value={searchQuery}
				/>
			</div>
			<button class="btn-primary" onclick={() => (showCreateDrawer = true)}>
				<Plus size={14} />
				New Loan
			</button>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-all">
			<Banknote size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total Loans</span>
			</div>
		</div>
		<div class="mini-stat s-pending">
			<Banknote size={18} />
			<div>
				<span class="mini-val">{stats.pending}</span>
				<span class="mini-lbl">Pending</span>
			</div>
		</div>
		<div class="mini-stat s-approved">
			<Banknote size={18} />
			<div>
				<span class="mini-val">{stats.approved}</span>
				<span class="mini-lbl">Approved</span>
			</div>
		</div>
		<div class="mini-stat s-rejected">
			<Banknote size={18} />
			<div>
				<span class="mini-val">{stats.rejected}</span>
				<span class="mini-lbl">Rejected</span>
			</div>
		</div>
	</div>

	<!-- Tabs as filter pills -->
	<div class="filter-row">
		{#each TABS as tab}
			<button
				class="filter-btn"
				class:active={activeTab === tab.key}
				onclick={() => switchTab(tab.key)}
			>
				{tab.label}
				{#if tab.key !== 'all'}
					<span class="count">({stats[tab.key as keyof typeof stats]})</span>
				{/if}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading loans…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredLoans.length === 0}
		<div class="empty-state">No loans found in this status.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredLoans as loan (loan.loan_id)}
				<tr
					class="clickable"
					onclick={() => {
						const target = loan.bank_approval_status === 'pending'
							? `/finance_staff/loans/${loan.loan_id}/review`
							: `/finance_staff/loans/${loan.loan_id}`;
						goto(target);
					}}
				>
					<td><span class="cell-id">#{loan.loan_id}</span></td>
					<td class="cell-name">{loan.customer_name}</td>
					<td class="cell-vehicle">{loan.brand} {loan.model}</td>
					<td class="cell-mono">{fmt(loan.loan_amount)}</td>
					<td class="cell-mono">{fmt(loan.down_payment)}</td>
					<td class="cell-mono">{loan.interest_rate}%</td>
					<td>{loan.term_months}mo</td>
					<td class="cell-mono">{fmt(loan.monthly_amortization)}</td>
					<td class="cell-bank">{loan.bank_name ?? '—'}</td>
					<td>
						<span class="badge badge-{loan.bank_approval_status}">{loan.bank_approval_status}</span>
					</td>
					<td>
						{#if loan.bank_approval_status === 'pending'}
							<a href="/finance_staff/loans/{loan.loan_id}/review" class="btn-link" onclick={(e) => e.stopPropagation()}>Review</a>
						{:else}
							<a href="/finance_staff/loans/{loan.loan_id}" class="btn-link" onclick={(e) => e.stopPropagation()}>View</a>
						{/if}
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<CreateLoanDrawer show={showCreateDrawer} onClose={handleDrawerClose} />

<style>
	.page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; align-items: start; flex-direction: column;}
	.logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid var(--border); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 12px; color: var(--text-primary); background: var(--bg-muted); outline: none; width: 200px; }
	.search-input:focus { border-color: var(--primary-light); background: var(--bg-card); }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: var(--bg-stat); border-radius: var(--radius-md); padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.mini-stat svg { flex-shrink: 0; }
	.s-all :global(svg) { color: var(--text-primary); }
	.s-pending :global(svg) { color: var(--warning); }
	.s-approved :global(svg) { color: #059669; }
	.s-rejected :global(svg) { color: var(--red); }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid var(--border); border-radius: 20px; background: var(--bg-muted); font-family: var(--font-sans); font-size: 11px; color: var(--text-light); cursor: pointer; transition: .15s; }
	.filter-btn.active { background: var(--primary); color: var(--accent); border-color: var(--primary); }
	.count { margin-left: 3px; opacity: 0.7; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: var(--danger); font-size: 13px; padding: 1rem; background: var(--danger-bg); border-radius: var(--radius-md); }
	.empty-state { text-align: center; padding: 2.5rem; color: var(--text-muted); font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--primary-light); }
	.cell-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
	.cell-vehicle { font-size: 12px; color: var(--text-dark); }
	.cell-mono { font-family: var(--font-mono); font-size: 11px; color: #059669; font-weight: 500; }
	.cell-bank { font-size: 11px; color: var(--text-light); }

	.clickable { cursor: pointer; transition: background .1s; }
	.clickable:hover { background: var(--bg-muted); }

	/* Status badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-pending { background: var(--warning-bg-light); color: var(--warning); }
	.badge-approved { background: #ecfdf5; color: #059669; }
	.badge-rejected { background: var(--red-bg); color: var(--red); }

	.btn-link { font-size: 11px; font-weight: 600; color: var(--primary-light); text-decoration: none; }
	.btn-link:hover { text-decoration: underline; }

	.btn-primary {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		height: 34px;
		padding: 0 14px;
		border: none;
		border-radius: var(--radius-md);
		background: var(--primary);
		color: var(--accent);
		font-family: var(--font-sans);
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s;
		white-space: nowrap;
	}
	.btn-primary:hover { opacity: 0.9; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
