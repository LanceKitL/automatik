<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import { getServiceStaffHistory } from '$lib/services/api';
	import { formatDateShort, formatSlotDateTime } from '$lib/utils/format';
	import { Loader } from '@lucide/svelte';

	let items = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);
	let total = $state(0);
	let page = $state(1);
	let perPage = $state(20);
	let totalPages = $derived(Math.ceil(total / perPage));
	let typeFilter = $state('');

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

	function badgeClass(t: string | null | undefined): string {
		if (!t) return 'badge-default';
		const v = t.toLowerCase();
		if (v === 'repair') return 'badge-repair';
		if (v === 'maintenance') return 'badge-maintenance';
		if (v === 'warranty') return 'badge-warranty';
		return 'badge-default';
	}

	onMount(() => loadPage(1));

	async function loadPage(p: number) {
		page = p;
		loading = true;
		try {
			const params: Record<string, unknown> = { page, per_page: perPage };
			if (typeFilter) params.type = typeFilter;
			const res = await getServiceStaffHistory(params as any);
			items = res.data as Record<string, unknown>[];
			total = res.total;
		} catch {
			toast.error('Failed to load history.');
			items = [];
			total = 0;
		} finally {
			loading = false;
		}
	}

	function setFilter(t: string) {
		typeFilter = t;
		loadPage(1);
	}

	let pages = $derived.by(() => {
		if (totalPages <= 5) return Array.from({ length: totalPages }, (_, i) => i + 1);
		const start = Math.max(1, page - 2);
		return Array.from({ length: 5 }, (_, i) => start + i).filter(p => p <= totalPages);
	});
</script>

<div class="dash">
	<div class="top-bar">
		<div class="logo-row">
			<h1>Service History</h1>
			<p class="subtitle">Record history, track your resolved vehicles.</p>
		</div>
	</div>

	<div class="tabs">
		<button class:active={typeFilter === ''} onclick={() => setFilter('')}>All</button>
		<button class:active={typeFilter === 'repair'} onclick={() => setFilter('repair')}>Repairs</button>
		<button class:active={typeFilter === 'maintenance'} onclick={() => setFilter('maintenance')}>Maintenance</button>
		<button class:active={typeFilter === 'warranty'} onclick={() => setFilter('warranty')}>Warranty</button>
	</div>

	{#if loading}
		<div class="loading-state"><div class="spinner"></div><span>Loading history…</span></div>
	{:else if items.length === 0}
		<div class="empty-state">No completed services found.</div>
	{:else}
		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Customer</th>
						<th>Vehicle</th>
						<th>Type</th>
						<th>Status</th>
						<th>Assigned To</th>
						<th>Date</th>
					</tr>
				</thead>
				<tbody>
					{#each items as entry}
						{@const h = entry as Record<string, unknown>}
						<tr>
							<td class="id-cell">{h.booking_id ?? h.claim_id}</td>
							<td>{h.customer_name ?? '—'}</td>
							<td>{String(h.brand ?? '')} {String(h.model ?? '')} ({String(h.year ?? '')})</td>
							<td><span class={badgeClass(h.entry_type as string)}>{(h.entry_type as string) ?? '—'}</span></td>
							<td><span class="status-badge {statusClass(h.status as string)}">{(h.status as string)?.replace(/_/g, ' ') ?? '—'}</span></td>
							<td>{h.assigned_to_name ?? h.reviewer_name ?? '—'}</td>
							<td>{h.slot_datetime ? formatSlotDateTime(h.slot_datetime as string) : h.resolved_at ? formatDateShort(h.resolved_at as string) : '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		{#if totalPages > 1}
			<div class="pagination">
				<button disabled={page <= 1} onclick={() => loadPage(page - 1)}>← Prev</button>
				{#each pages as p}
					<button class:active={p === page} onclick={() => loadPage(p)}>{p}</button>
				{/each}
				<button disabled={page >= totalPages} onclick={() => loadPage(page + 1)}>Next →</button>
			</div>
		{/if}
	{/if}
</div>

<style>
	.dash { padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; font-family: var(--font-sans); }

	.loading-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 40vh; gap: 1rem; color: var(--text-light); }
	.spinner { width: 28px; height: 28px; border: 2.5px solid var(--border); border-top-color: var(--primary); border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.empty-state { text-align: center; padding: 4rem 0; color: var(--text-muted); }

	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; }
	.logo-row { display: flex; flex-direction: column; align-items: start; justify-content: start; }
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	h1 { font-size: 24px; font-weight: 700; color: var(--text-primary); letter-spacing: -0.5px; margin: 0; }
	.count-pill { font-size: 12px; background: var(--bg-muted); color: var(--text-muted); padding: 2px 10px; border-radius: 12px; font-weight: 600; }

	.tabs { display: flex; gap: 4px; margin-bottom: 1.25rem; background: var(--bg-muted); padding: 3px; border-radius: var(--radius-sm); width: fit-content; }
	.tabs button { padding: 6px 14px; border: none; background: none; border-radius: var(--radius-sm); font-size: 12px; font-weight: 600; cursor: pointer; color: var(--text-muted); font-family: inherit; transition: all 0.15s; }
	.tabs button.active { background: var(--bg-card); color: var(--text-dark); box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
	.tabs button:hover:not(.active) { color: var(--text-dark); }

	.table-wrap { background: var(--bg-card); border-radius: var(--radius-lg); border: 0.5px solid var(--border); overflow: auto; }
	.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
	.data-table th { text-align: left; padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); background: var(--bg-muted); white-space: nowrap; }
	.data-table td { padding: 10px 14px; border-bottom: 1px solid var(--border); color: var(--text-primary); }
	.data-table tbody tr:hover { background: var(--bg-hover); }
	.data-table tbody tr:last-child td { border-bottom: none; }
	.id-cell { font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); white-space: nowrap; }

	.status-badge { font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; white-space: nowrap; }
	:global(.s-pending) { background: #fef3c7; color: #92400e; }
	:global(.s-confirmed) { background: #dbeafe; color: #1e40af; }
	:global(.s-review) { background: #e0e7ff; color: #3730a3; }
	:global(.s-progress) { background: #d1fae5; color: #065f46; }
	:global(.s-completed) { background: #d1fae5; color: #166534; }
	:global(.s-cancelled) { background: #fee2e2; color: #991b1b; }
	:global(.s-default) { background: var(--bg-muted); color: var(--text-muted); }

	:global(.badge-repair) { background: #dcfce7; color: #166534; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-maintenance) { background: #dbeafe; color: #1e40af; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-warranty) { background: #fef3c7; color: #92400e; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; text-transform: capitalize; }
	:global(.badge-default) { background: var(--bg-muted); color: var(--text-muted); font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; }

	.pagination { display: flex; align-items: center; justify-content: center; gap: 4px; margin-top: 1.25rem; }
	.pagination button { padding: 6px 12px; border: 0.5px solid var(--border); background: var(--bg-card); border-radius: var(--radius-sm); font-size: 12px; cursor: pointer; color: var(--text-dark); font-family: inherit; }
	.pagination button.active { background: var(--primary); color: var(--text-white); border-color: var(--primary); }
	.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
	.pagination button:hover:not(:disabled):not(.active) { background: var(--bg-hover); }
</style>
