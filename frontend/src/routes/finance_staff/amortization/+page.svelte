<script lang="ts">
	import { onMount } from 'svelte';
	import {
		getOverdueAmortizations,
		updateAmortizationStatus,
		type OverdueItem
	} from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';
	import { toast } from 'svelte-sonner';
	import { AlertTriangle, Search } from '@lucide/svelte';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let entries = $state<OverdueItem[]>([]);

	// ── Search ───────────────────────────────────────────────────────────────
	let searchQuery = $state('');

	let filteredEntries = $derived.by(() => {
		if (!searchQuery.trim()) return entries;
		const q = searchQuery.toLowerCase();
		return entries.filter(
			(e) =>
				String(e.schedule_id).includes(q) ||
				String(e.loan_id).includes(q) ||
				String(e.sale_id).includes(q) ||
				e.customer_name.toLowerCase().includes(q)
		);
	});

	// ── Stats ─────────────────────────────────────────────────────────────────
	let stats = $derived.by(() => {
		const totalAmount = entries.reduce((sum, e) => sum + Number(e.total_due || 0), 0);
		return { count: entries.length, totalAmount };
	});

	const tableColumns = [
		{ key: 'id', label: 'Schedule #' },
		{ key: 'loan', label: 'Loan ID' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'sale', label: 'Sale ID' },
		{ key: 'month', label: 'Month #' },
		{ key: 'due', label: 'Due Date' },
		{ key: 'amount', label: 'Amount Due' },
		{ key: 'status', label: 'Status' },
		{ key: 'actions', label: 'Actions' }
	];

	async function loadOverdue() {
		loading = true;
		error = null;
		try {
			const res = await getOverdueAmortizations();
			entries = res.data ?? [];
		} catch (e: unknown) {
			error = e instanceof Error ? e.message : 'Failed to load.';
		} finally {
			loading = false;
		}
	}

	async function handleMarkPaid(scheduleId: number) {
		if (!confirm('Mark this entry as paid?')) return;
		try {
			await updateAmortizationStatus(scheduleId, 'paid');
			toast.success(`Entry #${scheduleId} marked as paid.`);
			await loadOverdue();
		} catch (e: unknown) {
			toast.error(e instanceof Error ? e.message : 'Error marking as paid.');
		}
	}

	onMount(loadOverdue);

	function fmt(n: string | number | null | undefined): string {
		if (n == null) return '—';
		return `₱${Number(n).toLocaleString()}`;
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<h1>Overdue Amortizations</h1>
			<span style="color:var(--text-muted); margin-top:4px; font-size:14px">Manage overdue amortization payments</span>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by ID, customer…"
					bind:value={searchQuery}
				/>
			</div>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-count">
			<AlertTriangle size={18} />
			<div>
				<span class="mini-val">{stats.count}</span>
				<span class="mini-lbl">Overdue Entries</span>
			</div>
		</div>
		<div class="mini-stat s-amount">
			<AlertTriangle size={18} />
			<div>
				<span class="mini-val">{fmt(stats.totalAmount)}</span>
				<span class="mini-lbl">Total Amount Due</span>
			</div>
		</div>
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading overdue entries…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredEntries.length === 0}
		<div class="empty-state">No overdue amortizations.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredEntries as entry (entry.schedule_id)}
				<tr>
					<td><span class="cell-id">{entry.schedule_id}</span></td>
					<td><span class="cell-mono">#{entry.loan_id}</span></td>
					<td class="cell-name">{entry.customer_name}</td>
					<td><span class="cell-mono">#{entry.sale_id}</span></td>
					<td class="cell-mono">{entry.month_number}</td>
					<td>{entry.due_date ? String(entry.due_date).slice(0, 10) : '—'}</td>
					<td class="cell-mono">{fmt(entry.total_due)}</td>
					<td>
						<span class="badge badge-{entry.status?.toLowerCase() ?? 'overdue'}">{entry.status ?? 'overdue'}</span>
					</td>
					<td>
						<button class="btn-paid" onclick={() => handleMarkPaid(entry.schedule_id)}>Mark Paid</button>
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<style>
	.page { font-family: var(--font-sans); padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; align-items: start; flex-direction: column; }
	.logo-badge { width: 36px; height: 36px; background: var(--primary); border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: var(--accent); flex-shrink: 0; }
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-muted); pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid var(--border); border-radius: var(--radius-md); font-family: var(--font-sans); font-size: 12px; color: var(--text-primary); background: var(--bg-muted); outline: none; width: 200px; }
	.search-input:focus { border-color: var(--primary-light); background: var(--bg-card); }

	.msg { padding: 0.5rem 0.75rem; background: #ecfdf5; color: #059669; border-radius: var(--radius-sm); font-size: 13px; margin-bottom: 1rem; }

	.stats-row { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: var(--bg-stat); border-radius: var(--radius-md); padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.mini-stat :global(svg) { flex-shrink: 0; }
	.s-count :global(svg) { color: var(--red); }
	.s-amount :global(svg) { color: var(--warning); }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: var(--text-muted); letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: var(--text-muted); font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: var(--danger); font-size: 13px; padding: 1rem; background: var(--danger-bg); border-radius: var(--radius-md); }
	.empty-state { text-align: center; padding: 2.5rem; color: var(--text-muted); font-size: 13px; }

	.cell-id { font-family: var(--font-mono); font-size: 11px; font-weight: 600; color: var(--primary-light); }
	.cell-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
	.cell-mono { font-family: var(--font-mono); font-size: 11px; color: #059669; font-weight: 500; }

	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-overdue { background: var(--red-bg); color: var(--red); }
	.badge-unpaid { background: var(--warning-bg-light); color: var(--warning); }

	.btn-paid { padding: 4px 12px; border: none; border-radius: var(--radius-sm); background: var(--success); color: var(--text-white); font-family: var(--font-sans); font-size: 11px; font-weight: 600; cursor: pointer; transition: opacity .15s; }
	.btn-paid:hover { opacity: 0.85; }
</style>
