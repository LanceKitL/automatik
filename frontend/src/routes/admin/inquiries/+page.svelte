<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getInquiries } from '$lib/services/api';
	import type { InquiryItem } from '$lib/services/api';
	import InquiryDrawer from './InquiryDrawer.svelte';
	import { Search, MessageCircle, Clock, UserCheck, CheckCircle, Archive } from '@lucide/svelte';

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
		loading = true;
		error = null;
		try {
			const res = await getInquiries();
			rows = Array.isArray(res) ? (res as InquiryItem[]) : [];
		} catch (e) {
			toast.error((e as Error).message || 'Failed to load inquiries.');
			error = null;
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
		await loadInquiries();
	}

	onMount(loadInquiries);

	const FILTERS = ['all', 'open', 'assigned', 'resolved', 'closed'] as const;

	function formatDate(dateStr: string): string {
		if (!dateStr) return '—';
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
	}

	function filterLabel(f: string): string {
		return f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1);
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Inquiries</h1>
				<p class="title-subtitle">Review and manage customer inquiries</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by name, email, message, or ID…"
					bind:value={search}
				/>
			</div>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<MessageCircle size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total</span>
			</div>
		</div>
		<div class="mini-stat s-open">
			<Clock size={18} />
			<div>
				<span class="mini-val">{stats.open}</span>
				<span class="mini-lbl">Open</span>
			</div>
		</div>
		<div class="mini-stat s-assigned">
			<UserCheck size={18} />
			<div>
				<span class="mini-val">{stats.assigned}</span>
				<span class="mini-lbl">Assigned</span>
			</div>
		</div>
		<div class="mini-stat s-resolved">
			<CheckCircle size={18} />
			<div>
				<span class="mini-val">{stats.resolved}</span>
				<span class="mini-lbl">Resolved</span>
			</div>
		</div>
		<div class="mini-stat s-closed">
			<Archive size={18} />
			<div>
				<span class="mini-val">{stats.closed}</span>
				<span class="mini-lbl">Closed</span>
			</div>
		</div>
	</div>

	<!-- Filter pills -->
	<div class="filter-row">
		{#each FILTERS as f}
			<button
				class="filter-btn"
				class:active={activeFilter === f}
				onclick={() => (activeFilter = f)}
			>
				{filterLabel(f)}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading inquiries…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredRows.length === 0}
		<div class="empty-state">No inquiries found.</div>
	{:else}
		<DataTable columns={columns}>
			{#each filteredRows as row (row.inquiry_id)}
				<tr class="clickable" onclick={() => openDrawer(row)}>
					<td><span class="cell-id">#{row.inquiry_id}</span></td>
					<td class="cell-name">
						<span class="contact-name">{row.contacts.name ?? 'Guest'}</span>
						<span class="contact-email">{row.contacts.email ?? '—'}</span>
					</td>
					<td class="cell-vehicle">{row.vehicle.brand} {row.vehicle.model}</td>
					<td>
						<span class="badge badge-{row.status}">{row.status}</span>
					</td>
					<td class="cell-date">{formatDate(row.created_at)}</td>
					<td class="cell-agent">{row.agent_name ?? '—'}</td>
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
	.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-open :global(svg) { color: #4f46e5; flex-shrink: 0; }
	.s-assigned :global(svg) { color: #b45309; flex-shrink: 0; }
	.s-resolved :global(svg) { color: #059669; flex-shrink: 0; }
	.s-closed :global(svg) { color: #9ca3af; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter pills */
	.filter-row { display: flex; gap: 6px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.contact-name { font-weight: 600; color: #1a1a2e; }
	.contact-email { font-size: 10px; color: #9ca3af; display: block; margin-top: 1px; }
	.cell-vehicle { font-size: 12px; color: #374151; }
	.cell-date { font-size: 12px; color: #6b7280; }
	.cell-agent { font-size: 12px; color: #6b7280; }

	.clickable { cursor: pointer; transition: background .1s; }
	.clickable:hover { background: #f9fafb; }

	/* Status badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-open { background: #eef2ff; color: #4f46e5; }
	.badge-assigned { background: #fef3c7; color: #b45309; }
	.badge-resolved { background: #ecfdf5; color: #059669; }
	.badge-closed { background: #f3f4f6; color: #6b7280; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
