<script lang="ts">
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import DataTable from '$lib/components/DataTable.svelte';
	import {
		getSales,
		type SaleItem,
		type SaleListResponse
	} from '$lib/services/api';
	import { Archive, Plus, Search } from '@lucide/svelte';
	import CreateSaleDrawer from './CreateSaleDrawer.svelte';
	import SaleDetailDrawer from './SaleDetailDrawer.svelte';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let sales = $state<SaleItem[]>([]);

	// ── Filters & search ──────────────────────────────────────────────────────
	let searchQuery = $state('');
	let activeFilter = $state('all');
	const filters = ['all', 'pending', 'completed', 'cancelled'] as const;

	let filteredSales = $derived.by(() => {
		let list = sales;
		if (activeFilter !== 'all') {
			list = list.filter((s) => s.sales.status === activeFilter);
		}
		if (searchQuery.trim()) {
			const q = searchQuery.toLowerCase();
			list = list.filter(
				(s) =>
					String(s.sales.sale_id).includes(q) ||
					s.customer.username.toLowerCase().includes(q) ||
					s.vehicle.brand.toLowerCase().includes(q) ||
					s.vehicle.model.toLowerCase().includes(q)
			);
		}
		return list;
	});

	// ── Stats ──────────────────────────────────────────────────────────────────
	let stats = $derived({
		total: sales.length,
		pending: sales.filter((s) => s.sales.status === 'pending').length,
		completed: sales.filter((s) => s.sales.status === 'completed').length,
		cancelled: sales.filter((s) => s.sales.status === 'cancelled').length
	});

	const tableColumns = [
		{ key: 'id', label: 'Sale #' },
		{ key: 'customer', label: 'Customer' },
		{ key: 'vehicle', label: 'Vehicle' },
		{ key: 'price', label: 'Price' },
		{ key: 'payment', label: 'Payment' },
		{ key: 'status', label: 'Status' }
	];

	// ── Drawer state ───────────────────────────────────────────────────────────
	let showCreateDrawer = $state(false);
	let selectedSale = $state<SaleItem | null>(null);
	let showDetailDrawer = $state(false);

	function openDetail(sale: SaleItem) {
		selectedSale = sale;
		showDetailDrawer = true;
	}

	function handleCreated() {
		showCreateDrawer = false;
		loadSales();
	}

	async function loadSales() {
		loading = true;
		error = null;
		try {
			const res = await getSales();
			sales = res.data ?? [];
		} catch (e) {
			toast.error((e as Error).message || 'Failed to load sales.');
			error = null;
		} finally {
			loading = false;
		}
	}

	onMount(loadSales);
</script>

<div class="page">
	<!-- Top bar -->
	<div class="top-bar">
		<div class="title-row">
			<div>
				<h1>Sales Management</h1>
				<p class="title-subtitle">Manage vehicle sales and contracts</p>
			</div>
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
			<button class="create-btn" onclick={() => (showCreateDrawer = true)}>
				<Plus size={14} />New Sale
			</button>
		</div>
	</div>

	<!-- Mini stats -->
	<div class="stats-row">
		<div class="mini-stat s-all">
			<Archive size={18} />
			<div>
				<span class="mini-val">{stats.total}</span>
				<span class="mini-lbl">Total Sales</span>
			</div>
		</div>
		<div class="mini-stat s-pending">
			<Archive size={18} />
			<div>
				<span class="mini-val">{stats.pending}</span>
				<span class="mini-lbl">Pending</span>
			</div>
		</div>
		<div class="mini-stat s-completed">
			<Archive size={18} />
			<div>
				<span class="mini-val">{stats.completed}</span>
				<span class="mini-lbl">Completed</span>
			</div>
		</div>
		<div class="mini-stat s-cancelled">
			<Archive size={18} />
			<div>
				<span class="mini-val">{stats.cancelled}</span>
				<span class="mini-lbl">Cancelled</span>
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
				{f.charAt(0).toUpperCase() + f.slice(1)}
			</button>
		{/each}
	</div>

	<!-- Loading / Error / Empty / Table -->
	{#if loading}
		<div class="loading-state">
			<div class="spinner"></div>
			<span>Loading sales…</span>
		</div>
	{:else if error}
		<div class="error-msg">{error}</div>
	{:else if filteredSales.length === 0}
		<div class="empty-state">No sales found.</div>
	{:else}
		<DataTable columns={tableColumns}>
			{#each filteredSales as s (s.sales.sale_id)}
				<tr class="clickable" onclick={() => openDetail(s)}>
					<td><span class="cell-id">#{s.sales.sale_id}</span></td>
					<td class="cell-name">{s.customer.username}</td>
					<td class="cell-vehicle">{s.vehicle.brand} {s.vehicle.model}</td>
					<td><span class="cell-price">${Number(s.sales.selling_price || s.vehicle.price).toLocaleString()}</span></td>
					<td><span class="cell-payment">{s.sales.payment_type}</span></td>
					<td>
						<span class="badge badge-{s.sales.status}">{s.sales.status}</span>
					</td>
				</tr>
			{/each}
		</DataTable>
	{/if}
</div>

<!-- ─── Drawers ─────────────────────────────────────────────────────── -->
{#if showCreateDrawer}
	<CreateSaleDrawer
		onclose={() => (showCreateDrawer = false)}
		oncreated={handleCreated}
	/>
{/if}

{#if showDetailDrawer && selectedSale}
	<SaleDetailDrawer
		sale={selectedSale}
		onclose={() => {
			showDetailDrawer = false;
			selectedSale = null;
		}}
		onupdated={loadSales}
	/>
{/if}

<style>
	@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

	.page { font-family: 'Syne', sans-serif; padding: 2rem 1.5rem; max-width: 1500px; margin: 0 auto; }

	/* Top bar */
	.top-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.75rem; flex-wrap: wrap; gap: 10px; }
	.title-row { display: flex; align-items: center; gap: 10px; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	.logo-badge { width: 36px; height: 36px; background: #1a1a2e; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 17px; font-weight: 700; color: #e8c97e; flex-shrink: 0; }
	h1 { font-size: 20px; font-weight: 700; color: #1a1a2e; letter-spacing: -0.5px; margin: 0; }
	.toolbar { display: flex; align-items: center; gap: 10px; }
	.search-wrap { position: relative; }
	.search-wrap :global(.search-icon) { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: #9ca3af; pointer-events: none; }
	.search-input { height: 34px; padding: 0 12px 0 32px; border: 0.5px solid #e5e7eb; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; color: #1a1a2e; background: #f9fafb; outline: none; width: 200px; }
	.search-input:focus { border-color: #7c9df7; background: #fff; }
	.create-btn { display: flex; align-items: center; gap: 6px; height: 34px; padding: 0 14px; background: #1a1a2e; color: #e8c97e; border: none; border-radius: 8px; font-family: 'Syne', sans-serif; font-size: 12px; font-weight: 600; cursor: pointer; letter-spacing: 0.2px; transition: opacity .15s; }
	.create-btn:hover { opacity: 0.85; }

	/* Mini stats */
	.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 1.25rem; }
	.mini-stat { background: #f8f7f4; border-radius: 10px; padding: .75rem 1rem; display: flex; align-items: center; gap: 10px; }
  .s-all :global(svg) { color: #1a1a2e; flex-shrink: 0; }
  .s-pending :global(svg) { color: #b45309; flex-shrink: 0; }
  .s-completed :global(svg) { color: #059669; flex-shrink: 0; }
  .s-cancelled :global(svg) { color: #dc2626; flex-shrink: 0; }
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
	.error-msg { color: #A32D2D; font-size: 13px; padding: 1rem; background: #FCEBEB; border-radius: 8px; }
	.empty-state { text-align: center; padding: 2.5rem; color: #9ca3af; font-size: 13px; }

	/* Table cells */
	.cell-id { font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 600; color: #7c9df7; }
	.cell-name { font-size: 13px; font-weight: 600; color: #1a1a2e; }
	.cell-vehicle { font-size: 12px; color: #374151; }
	.cell-price { font-family: 'DM Mono', monospace; font-size: 12px; color: #059669; font-weight: 500; }
	.cell-payment { font-size: 11px; color: #6b7280; background: #f3f4f6; padding: 2px 8px; border-radius: 4px; text-transform: capitalize; }

	.clickable { cursor: pointer; transition: background .1s; }
	.clickable:hover { background: #f9fafb; }

	/* Status badges */
	.badge { display: inline-flex; align-items: center; padding: 3px 9px; border-radius: 20px; font-size: 10px; font-weight: 600; letter-spacing: 0.4px; text-transform: uppercase; }
	.badge-pending { background: var(--warning-bg-light); color: var(--warning); }
	.badge-completed { background: #ecfdf5; color: #059669; }
	.badge-cancelled { background: var(--red-bg); color: var(--red); }

	@media (max-width: 640px) {
		.stats-row { grid-template-columns: 1fr 1fr; }
		.top-bar { flex-direction: column; align-items: flex-start; }
	}
</style>
