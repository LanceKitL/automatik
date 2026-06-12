<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getInquiries } from '$lib/services/api';
	import type { InquiryItem } from '$lib/services/api';
	import InquiryDrawer from './InquiryDrawer.svelte';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<InquiryItem[]>([]);
	let search = $state('');
	let activeFilter = $state<'all' | 'open' | 'assigned' | 'resolved' | 'closed'>('all');

	let selectedInquiry = $state<InquiryItem | null>(null);
	let showDrawer = $state(false);

	const columns = [
		{ key: 'inquiry_id', label: 'ID' },
		{ key: 'contacts', label: 'Contact' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'status', label: 'Status' },
		{ key: 'created_at', label: 'Created' },
		{ key: 'agent_name', label: 'Assigned Agent' },
	];

	let stats = $derived({
		total: rows.length,
		open: rows.filter((r) => r.status === 'open').length,
		assigned: rows.filter((r) => r.status === 'assigned').length,
		resolved: rows.filter((r) => r.status === 'resolved').length,
		closed: rows.filter((r) => r.status === 'closed').length,
	});

	let filteredRows = $derived(
		rows.filter((r) => {
			const matchStatus = activeFilter === 'all' || r.status === activeFilter;
			const s = search.toLowerCase();
			const matchSearch =
				!s ||
				String(r.contacts.name ?? '').toLowerCase().includes(s) ||
				String(r.contacts.email ?? '').toLowerCase().includes(s) ||
				String(r.message).toLowerCase().includes(s) ||
				String(r.inquiry_id).includes(s);
			return matchStatus && matchSearch;
		})
	);

	async function loadInquiries() {
		try {
			const res = await getInquiries();
			rows = Array.isArray(res) ? (res as InquiryItem[]) : [];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	function openDrawer(inquiry: InquiryItem) {
		selectedInquiry = inquiry;
		showDrawer = true;
	}

	function closeDrawer() {
		showDrawer = false;
		selectedInquiry = null;
	}

	async function onInquiryUpdated() {
		selectedInquiry = null;
		showDrawer = false;
		loading = true;
		await loadInquiries();
	}

	onMount(loadInquiries);

	const FILTERS = ['all', 'open', 'assigned', 'resolved', 'closed'] as const;

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<h1>Inquiries</h1>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
				</svg>
				<input
					class="search-input"
					type="text"
					placeholder="Search by name, email, message, or ID…"
					bind:value={search}
				/>
			</div>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<span class="mini-val">{stats.total}</span>
			<span class="mini-lbl">Total</span>
		</div>
		<div class="mini-stat s-open">
			<span class="mini-val">{stats.open}</span>
			<span class="mini-lbl">Open</span>
		</div>
		<div class="mini-stat s-assigned">
			<span class="mini-val">{stats.assigned}</span>
			<span class="mini-lbl">Assigned</span>
		</div>
		<div class="mini-stat s-resolved">
			<span class="mini-val">{stats.resolved}</span>
			<span class="mini-lbl">Resolved</span>
		</div>
		<div class="mini-stat s-closed">
			<span class="mini-val">{stats.closed}</span>
			<span class="mini-lbl">Closed</span>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each FILTERS as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => activeFilter = f}
			>
				{f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
			</button>
		{/each}
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="loading-state">
			<span class="spinner"></span>
			<p>Loading inquiries…</p>
		</div>
	<!-- Error state -->
	{:else if error}
		<div class="error-msg">
			<p>{error}</p>
		</div>
	<!-- Table -->
	{:else}
		<DataTable columns={columns}>
			{#each filteredRows as row (row.inquiry_id)}
				<tr class="clickable-row" onclick={() => openDrawer(row)}>
					<td class="cell-id">#{row.inquiry_id}</td>
					<td class="cell-contact">
						<span class="contact-name">{row.contacts.name ?? 'Guest'}</span>
						<span class="contact-email">{row.contacts.email ?? '—'}</span>
					</td>
					<td class="cell-vehicle">
						{row.vehicle.brand} {row.vehicle.model}
					</td>
					<td>
						<span class="badge badge-{row.status}">{row.status}</span>
					</td>
					<td class="cell-date">{formatDate(row.created_at)}</td>
					<td class="cell-agent">
						{row.agent_name ?? '—'}
					</td>
				</tr>
			{:else}
				<tr>
					<td colspan="6" class="empty-state">No inquiries found.</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<InquiryDrawer
	show={showDrawer}
	inquiry={selectedInquiry}
	onclose={closeDrawer}
	onupdated={onInquiryUpdated}
/>

<style>
	.page {
    font-family: var(--font-sans); 
	padding: 2rem 1.5rem; 
	max-width: 1500px; 
	margin: 0 auto;
	}

	/* ── Top bar ────────────────────────────────── */
	.top-bar { margin-bottom: 1.5rem; }
	.title-row h1 { margin: 0 0 1rem; font-size: 1.5rem; color: var(--text-primary); }
	.toolbar { display: flex; align-items: center; gap: 0.75rem; }
	.search-wrap {
		position: relative; flex: 1; max-width: 28rem;
	}
	.search-icon {
		position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%);
		color: var(--text-muted); pointer-events: none;
	}
	.search-input {
		width: 100%; padding: 0.55rem 0.75rem 0.55rem 2.25rem;
		border: 1px solid #d1d5db; border-radius: var(--radius-sm); font-size: 0.875rem;
		background: var(--bg-card);
	}
	.search-input:focus { outline: none; border-color: var(--primary-light); box-shadow: 0 0 0 2px rgba(124,157,247,0.15); }

	/* ── Mini stats ─────────────────────────────── */
	.stats-row {
		display: flex; gap: 1rem; margin-bottom: 1.25rem;
	}
	.mini-stat {
		flex: 1; padding: 1rem 1.25rem; border-radius: var(--radius-md); border: 1px solid var(--border);
		background: var(--bg-card); position: relative; overflow: hidden;
	}
	.mini-stat::before {
		content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%;
	}
	.mini-val { display: block; font-size: 1.75rem; font-weight: 700; line-height: 1.1; }
	.mini-lbl { font-size: 0.8rem; color: var(--text-light); margin-top: 0.25rem; display: block; }
	.s-total::before { background: var(--text-light); }
	.s-open::before { background: var(--primary-light); }
	.s-assigned::before { background: var(--accent); }
	.s-resolved::before { background: #6de0b0; }
	.s-closed::before { background: var(--text-muted); }

	/* ── Filter pills ────────────────────────────── */
	.filter-row { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn {
		padding: 0.4rem 0.9rem; font-size: 0.8rem; font-weight: 500;
		border: 1px solid #d1d5db; border-radius: 20px; background: var(--bg-card);
		color: var(--text-dark); cursor: pointer; transition: all 0.15s;
	}
	.filter-btn.active {
		background: var(--primary); color: var(--accent); border-color: var(--primary);
	}
	.filter-btn:hover:not(.active) { border-color: var(--primary-light); color: var(--primary-light); }

	/* ── Table styling ──────────────────────────── */
	:global(table) { font-size: 0.85rem; }
	.clickable-row { cursor: pointer; transition: background 0.1s; }
	.clickable-row:hover { background: var(--primary-bg); }
  .cell-id { font-family: var(--font-mono); font-weight: 600; color: var(--primary-light); }
	.cell-contact { display: flex; flex-direction: column; gap: 0.15rem; }
	.contact-name { font-weight: 600; color: var(--text-primary); }
	.contact-email { font-size: 0.75rem; color: var(--text-muted); }
	.cell-vehicle { font-weight: 500; }
	.cell-date { font-size: 0.8rem; color: var(--text-light); }
	.cell-agent { font-size: 0.8rem; }

	/* ── Status badges ──────────────────────────── */
	:global(.badge) {
		display: inline-block; padding: 2px 10px; border-radius: 12px;
		font-size: 0.7rem; font-weight: 600; text-transform: capitalize;
	}
	:global(.badge-open) { background: #eef2ff; color: #4f46e5; }
	:global(.badge-assigned) { background: var(--warning-bg-light); color: var(--warning); }
	:global(.badge-resolved) { background: #ecfdf5; color: #059669; }
	:global(.badge-closed) { background: var(--bg-hover); color: var(--text-light); }

	/* ── States ──────────────────────────────────── */
	.loading-state { display: flex; align-items: center; gap: 0.75rem; padding: 2rem; color: var(--text-light); }
	.spinner {
		width: 1.25rem; height: 1.25rem; border: 2px solid var(--border);
		border-top-color: var(--primary-light); border-radius: 50%; animation: spin 0.6s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg {
		background: var(--danger-bg); color: var(--danger); padding: 1rem; border-radius: var(--radius-sm); margin: 1rem 0;
	}
	.empty-state { text-align: center; padding: 2rem; color: var(--text-muted); font-style: italic; }
</style>
