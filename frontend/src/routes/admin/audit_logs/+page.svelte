<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getAuditLogs } from '$lib/services/api';
	import type { ListResponse } from '$lib/services/api';
	import { Search, ClipboardList, Users, Database, X } from '@lucide/svelte';

	interface AuditLogItem {
		log_id: number;
		user_id: number;
		action: string;
		table_name: string;
		record_id: number | null;
		created_at: string;
		username: string;
	}

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<AuditLogItem[]>([]);

	// Search & filters
	let searchQuery = $state('');
	let selectedUser = $state('All Users');
	let selectedTable = $state('All Tables');
	let actionFilter = $state('All');
	let dateFrom = $state('');
	let dateTo = $state('');

	const actions = ['All', 'POST', 'PUT', 'DELETE'] as const;

	// Stats derived from data
	let stats = $derived({
		total: rows.length,
		uniqueUsers: new Set(rows.map(r => r.username)).size,
		uniqueTables: new Set(rows.map(r => r.table_name)).size,
	});

	// Dropdown options
	let uniqueUsers = $derived([...new Set(rows.map(r => r.username))].filter(Boolean).sort());
	let uniqueTables = $derived([...new Set(rows.map(r => r.table_name))].filter(Boolean).sort());

	// Client-side filtering
	let filteredRows = $derived.by(() => {
		let list = rows;
		if (selectedUser !== 'All Users') list = list.filter(r => r.username === selectedUser);
		if (selectedTable !== 'All Tables') list = list.filter(r => r.table_name === selectedTable);
		if (actionFilter !== 'All') list = list.filter(r => r.action === actionFilter);
		if (dateFrom) list = list.filter(r => new Date(r.created_at) >= new Date(dateFrom));
		if (dateTo) {
			const end = new Date(dateTo + 'T23:59:59');
			list = list.filter(r => new Date(r.created_at) <= end);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(r =>
				r.action.toLowerCase().includes(q) ||
				r.table_name.toLowerCase().includes(q) ||
				r.username?.toLowerCase().includes(q)
			);
		}
		return list;
	});

	const columns = [
		{ key: 'log_id', label: 'ID' },
		{ key: 'username', label: 'User' },
		{ key: 'action', label: 'Action' },
		{ key: 'table_name', label: 'Table' },
		{ key: 'record_id', label: 'Record ID' },
		{ key: 'created_at', label: 'Timestamp' },
	];

	function getSelectedUserId(): number | undefined {
		if (selectedUser === 'All Users') return undefined;
		const match = rows.find(r => r.username === selectedUser);
		return match?.user_id;
	}

	function buildQueryString(): string {
		const p = new URLSearchParams();
		const uid = getSelectedUserId();
		if (uid !== undefined) p.set('user_id', String(uid));
		if (selectedTable !== 'All Tables') p.set('table_name', selectedTable);
		if (actionFilter !== 'All') p.set('action', actionFilter);
		if (dateFrom) p.set('date_from', dateFrom);
		if (dateTo) p.set('date_to', dateTo);
		const s = p.toString();
		return s ? `?${s}` : '';
	}

	async function loadAuditLogs() {
		loading = true;
		error = null;
		try {
			const res = await getAuditLogs(buildQueryString());
			rows = (res.data ?? []) as AuditLogItem[];
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	}

	onMount(loadAuditLogs);

	function clearSearch() {
		searchQuery = '';
	}

	function formatTimestamp(dateStr: string): string {
		if (!dateStr) return '—';
		return new Date(dateStr).toLocaleString();
	}
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Audit Log</h1>
				<p class="title-subtitle">Track all system activities and user actions</p>
			</div>
		</div>
		<div class="toolbar">
			<div class="search-wrap">
				<Search class="search-icon" size={14} />
				<input
					type="text"
					class="search-input"
					placeholder="Search by action, table, user…"
					bind:value={searchQuery}
				/>
				{#if searchQuery}
					<button class="clear-btn" onclick={clearSearch}>
						<X size={14} />
					</button>
				{/if}
			</div>
		</div>
	</div>

	<!-- Stats row -->
	<div class="stats-row">
		<div class="mini-stat s-total">
			<ClipboardList size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total Entries</span>
			</div>
		</div>
		<div class="mini-stat s-users">
			<Users size={18} />
			<div>
				<span class="mini-val">{stats.uniqueUsers}</span>
				<span class="mini-lbl">Unique Users</span>
			</div>
		</div>
		<div class="mini-stat s-tables">
			<Database size={18} />
			<div>
				<span class="mini-val">{stats.uniqueTables}</span>
				<span class="mini-lbl">Unique Tables</span>
			</div>
		</div>
	</div>

	<!-- Filter row -->
	<div class="filter-row">
		<select class="filter-select" bind:value={selectedUser}>
			<option>All Users</option>
			{#each uniqueUsers as u}
				<option>{u}</option>
			{/each}
		</select>

		<select class="filter-select" bind:value={selectedTable}>
			<option>All Tables</option>
			{#each uniqueTables as t}
				<option>{t}</option>
			{/each}
		</select>

		<div class="pills-wrap">
			{#each actions as a}
				<button
					class="filter-btn"
					class:active={actionFilter === a}
					onclick={() => (actionFilter = a)}
				>
					{a}
				</button>
			{/each}
		</div>

		<div class="date-range">
			<input type="date" class="date-input" bind:value={dateFrom} />
			<span class="date-sep">—</span>
			<input type="date" class="date-input" bind:value={dateTo} />
		</div>
	</div>

	<!-- Content area -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading audit logs…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredRows.length === 0}
		<div class="empty-state">No audit log entries found.</div>
	{:else}
		<DataTable columns={columns}>
			{#each filteredRows as row (row.log_id)}
				<tr class="clickable">
					<td><span class="cell-id">#{row.log_id}</span></td>
					<td class="cell-user">{row.username}</td>
					<td><span class="action-badge badge-{row.action.toLowerCase()}">{row.action}</span></td>
					<td><span class="table-pill">{row.table_name}</span></td>
					<td>{row.record_id ?? '—'}</td>
					<td class="cell-ts">{formatTimestamp(row.created_at)}</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

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
	.search-input { height: 34px; padding: 0 32px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 220px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }
	.clear-btn { position: absolute; right: 6px; top: 50%; transform: translateY(-50%); background: none; border: none; cursor: pointer; color: #9ca3af; padding: 2px; display: flex; align-items: center; border-radius: 4px; }
	.clear-btn:hover { color: #1a1a2e; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
	.s-total :global(svg) { color: #1a1a2e; flex-shrink: 0; }
	.s-users :global(svg) { color: #7c3aed; flex-shrink: 0; }
	.s-tables :global(svg) { color: #059669; flex-shrink: 0; }
	.mini-stat div { display: flex; flex-direction: column; }
	.mini-val { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; line-height: 1; }
	.mini-lbl { font-size: 10px; font-weight: 500; color: #9ca3af; letter-spacing: 0.6px; text-transform: uppercase; margin-top: 2px; }

	/* Filter row */
	.filter-row { display: flex; align-items: center; gap: 8px; margin-bottom: 1rem; flex-wrap: wrap; }
	.filter-select { height: 30px; padding: 0 24px 0 10px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 11px; color: #374151; background: #f9fafb; outline: none; cursor: pointer; appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 6px center; }
	.filter-select:focus { border-color: #7c9df7; background-color: #fff; }
	.pills-wrap { display: flex; gap: 4px; }
	.filter-btn { height: 28px; padding: 0 12px; border: 0.5px solid #e5e7eb; border-radius: 20px; background: #f9fafb; font-family: 'Syne', sans-serif; font-size: 11px; color: #6b7280; cursor: pointer; transition: .15s; text-transform: uppercase; letter-spacing: 0.3px; }
	.filter-btn.active { background: #1a1a2e; color: #e8c97e; border-color: #1a1a2e; }
	.date-range { display: flex; align-items: center; gap: 4px; }
	.date-input { height: 30px; padding: 0 8px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 11px; color: #374151; background: #f9fafb; outline: none; }
	.date-input:focus { border-color: #7c9df7; background: #fff; }
	.date-sep { color: #9ca3af; font-size: 12px; }

	/* Loading & Error */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 3rem; color: #9ca3af; font-size: 13px; }
	.spinner { width: 24px; height: 24px; border: 2px solid #e5e7eb; border-top-color: #1a1a2e; border-radius: 50%; animation: spin .7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; margin-bottom: 1rem; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-user { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.cell-ts { font-size: 12px; color: #6b7280; }

	.clickable { cursor: pointer; transition: background .1s; }
	.clickable:hover { background: #f9fafb; }

	/* Action badges */
	.action-badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-get { background: #eef2ff; color: #4f46e5; }
	.badge-post { background: #ecfdf5; color: #059669; }
	.badge-put { background: #fef3c7; color: #b45309; }
	.badge-delete { background: #fef2f2; color: #dc2626; }

	/* Table pill */
	.table-pill { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; padding: 2px 8px; border-radius: 4px; background: #f3f4f6; color: #374151; text-transform: uppercase; letter-spacing: 0.3px; }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
		.filter-row { flex-direction: column; align-items: stretch; }
	}
</style>
