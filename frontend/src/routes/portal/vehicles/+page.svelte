<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerPortalVehicles, resolvePhotoUrl } from '$lib/services/api';
	import type { VehicleItem } from '$lib/services/api';
	import { Search } from '@lucide/svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let vehicles = $state<VehicleItem[]>([]);
	let loading = $state(true);
	let search = $state('');
	let selectedBody = $state('');
	let selectedTrans = $state('');
	let selectedFuel = $state('');
	let selectedBrand = $state('');

	let vehicleMinPrice = $state(0);
	let vehicleMaxPrice = $state(99999999);
	let priceMin = $state(0);
	let priceMax = $state(99999999);
	let priceModalOpen = $state(false);
	let draftMin = $state(0);
	let draftMax = $state(99999999);

	let initialized = $state(false);

	const bodyOptions = ['Sedan', 'SUV'];
	const transOptions = ['Manual', 'Automatic'];
	const fuelOptions = ['Gasoline', 'Diesel'];
	const brandOptions = ['BYD', 'Honda', 'Hyundai', 'Toyota'];

	let filtered = $derived(
		vehicles.filter((v) => {
			const q = search.toLowerCase();
			if (q && !`${v.brand} ${v.model} ${v.year} ${v.color ?? ''} ${v.body_type ?? ''}`
				.toLowerCase().includes(q)) return false;
			if (selectedBody && (v.body_type ?? '').toLowerCase() !== selectedBody.toLowerCase()) return false;
			if (selectedTrans && (v.transmission ?? '').toLowerCase() !== selectedTrans.toLowerCase()) return false;
			if (selectedFuel && (v.fuel_type ?? '').toLowerCase() !== selectedFuel.toLowerCase()) return false;
			if (selectedBrand && v.brand !== selectedBrand) return false;
			const price = Number(v.price);
			if (price < priceMin) return false;
			if (price > priceMax) return false;
			return true;
		})
	);

	onMount(async () => {
		// Read filter values from URL query params
		const url = $page.url;
		search = url.searchParams.get('q') || '';
		selectedBody = url.searchParams.get('body') || '';
		selectedTrans = url.searchParams.get('trans') || '';
		selectedFuel = url.searchParams.get('fuel') || '';
		selectedBrand = url.searchParams.get('brand') || '';
		const urlPmin = url.searchParams.get('pmin');
		const urlPmax = url.searchParams.get('pmax');

		try {
			const res = await getCustomerPortalVehicles();
			vehicles = res.data;
			const prices = vehicles.map((v) => Number(v.price));
			vehicleMinPrice = Math.min(...prices);
			vehicleMaxPrice = Math.max(...prices);
			priceMin = urlPmin ? Number(urlPmin) : vehicleMinPrice;
			priceMax = urlPmax ? Number(urlPmax) : vehicleMaxPrice;
		} catch {
			vehicles = [];
		} finally {
			loading = false;
			initialized = true;
		}
	});

	// Sync filter state to URL so it survives navigation away and back
	$effect(() => {
		if (!initialized) return;
		const params = new URLSearchParams();
		if (search) params.set('q', search);
		if (selectedBody) params.set('body', selectedBody);
		if (selectedTrans) params.set('trans', selectedTrans);
		if (selectedFuel) params.set('fuel', selectedFuel);
		if (selectedBrand) params.set('brand', selectedBrand);
		if (priceMin !== vehicleMinPrice) params.set('pmin', String(priceMin));
		if (priceMax !== vehicleMaxPrice) params.set('pmax', String(priceMax));
		const qs = params.toString();
		const newSearch = qs ? `?${qs}` : '';
		if (window.location.search !== newSearch) {
			history.replaceState(null, '', newSearch || window.location.pathname);
		}
	});

	function openPriceModal() {
		draftMin = priceMin;
		draftMax = priceMax;
		priceModalOpen = true;
	}

	function applyPrice() {
		priceMin = Math.min(draftMin, draftMax);
		priceMax = Math.max(draftMin, draftMax);
		priceModalOpen = false;
	}

	function clearPrice() {
		priceMin = vehicleMinPrice;
		priceMax = vehicleMaxPrice;
		priceModalOpen = false;
	}

	function formatPrice(p: string) {
		return `₱${Number(p).toLocaleString()}`;
	}

	function formatShort(p: number) {
		if (p >= 1000000) return `${(p / 1000000).toFixed(1)}M`;
		if (p >= 1000) return `${(p / 1000).toFixed(0)}K`;
		return p.toLocaleString();
	}

	function priceActive() {
		return priceMin !== vehicleMinPrice || priceMax !== vehicleMaxPrice;
	}

	function getPhotoUrl(v: VehicleItem, idx: number) {
		return resolvePhotoUrl(v.photos?.[idx]?.photo_url ?? null);
	}
</script>

<h1>Browse Vehicles</h1>

<div class="toolbar">
	<div class="search-wrap">
		<span class="search-icon-wrap"><Search size={16} /></span>
		<input type="text" bind:value={search} placeholder="Search by brand, model, or year…" />
	</div>
	<button class="price-btn" class:active={priceActive()} onclick={openPriceModal}>
		<span class="price-btn-label">Price</span>
		<span class="price-btn-range">
			₱{formatShort(priceMin)} – ₱{formatShort(priceMax)}
		</span>
	</button>
</div>

{#if priceModalOpen}
	<!-- svelte-ignore a11y_no_static_element_interactions -->
	<div class="modal-backdrop" onclick={() => priceModalOpen = false} />
	<div class="modal" role="dialog">
		<h3>Set Price Range</h3>
		<div class="modal-fields">
			<label>
				Min Price (₱)
				<input type="number" bind:value={draftMin} min={vehicleMinPrice} max={vehicleMaxPrice} step={50000} />
			</label>
			<label>
				Max Price (₱)
				<input type="number" bind:value={draftMax} min={vehicleMinPrice} max={vehicleMaxPrice} step={50000} />
			</label>
		</div>
		<div class="modal-actions">
			<button class="btn-apply" onclick={applyPrice}>Apply</button>
			<button class="btn-clear" onclick={clearPrice}>Clear</button>
			<button class="btn-cancel" onclick={() => priceModalOpen = false}>Cancel</button>
		</div>
	</div>
{/if}

<div class="pills">
	<button class="pill" class:active={selectedBody === ''} onclick={() => selectedBody = ''}>All Bodies</button>
	{#each bodyOptions as b}
		<button class="pill" class:active={selectedBody === b} onclick={() => selectedBody = b}>{b}</button>
	{/each}
	<span class="pill-sep" />
	<button class="pill" class:active={selectedTrans === ''} onclick={() => selectedTrans = ''}>All Trans</button>
	{#each transOptions as t}
		<button class="pill" class:active={selectedTrans === t} onclick={() => selectedTrans = t}>{t}</button>
	{/each}
	<span class="pill-sep" />
	<button class="pill" class:active={selectedFuel === ''} onclick={() => selectedFuel = ''}>All Fuel</button>
	{#each fuelOptions as f}
		<button class="pill" class:active={selectedFuel === f} onclick={() => selectedFuel = f}>{f}</button>
	{/each}
	<span class="pill-sep" />
	<button class="pill" class:active={selectedBrand === ''} onclick={() => selectedBrand = ''}>All Brands</button>
	{#each brandOptions as b}
		<button class="pill" class:active={selectedBrand === b} onclick={() => selectedBrand = b}>{b}</button>
	{/each}
</div>

{#if loading}
	<p class="loading">Loading vehicles…</p>
{:else if filtered.length === 0}
	<p class="empty">No vehicles match your criteria.</p>
{:else}
	<div class="grid">
		{#each filtered as v}
			<button class="card" onclick={() => goto(`/portal/vehicles/${v.vehicle_id}`)}>
				<div class="card-img">
					{#if getPhotoUrl(v, 0)}
						<img src={getPhotoUrl(v, 0)} alt="{v.brand} {v.model}" />
					{:else}
						<div class="no-photo">No Image</div>
					{/if}
				</div>
				<div class="card-body">
					<div class="card-title">{v.brand} {v.model}</div>
					<div class="card-sub">{v.year} &middot; {v.color ?? 'N/A'}</div>
					<div class="card-price">{formatPrice(v.price)}</div>
					<div class="card-specs">
						<span>{v.transmission}</span>
						<span>{v.fuel_type}</span>
						<span>{v.body_type}</span>
					</div>
				</div>
			</button>
		{/each}
	</div>
{/if}

<style>
	h1 {
		font-size: 24px;
		font-weight: 700;
		margin-bottom: 20px;
		color: var(--text-dark);
	}

	.toolbar {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 16px;
	}
	.search-wrap {
		flex: 1;
		position: relative;
	}
	.search-icon-wrap {
		position: absolute;
		left: 12px;
		top: 50%;
		transform: translateY(-50%);
		color: var(--text-muted);
		pointer-events: none;
		display: flex;
		align-items: center;
	}
	.search-wrap input {
		width: 100%;
		padding: 10px 12px 10px 36px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		font-size: 14px;
		background: var(--bg-card);
		outline: none;
		box-sizing: border-box;
		font-family: inherit;
	}
	.search-wrap input:focus {
		border-color: var(--blue);
		box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
	}
	.price-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 14px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--bg-card);
		cursor: pointer;
		font-family: inherit;
		font-size: 13px;
		transition: all 0.15s;
		flex-shrink: 0;
	}
	.price-btn:hover {
		border-color: var(--blue);
	}
	.price-btn.active {
		border-color: var(--blue);
		background: var(--blue-bg);
	}
	.price-btn-label {
		font-weight: 600;
		color: var(--text-dark);
	}
	.price-btn.active .price-btn-label {
		color: #1d4ed8;
	}
	.price-btn-range {
		color: var(--text-muted);
		font-size: 12px;
	}
	.price-btn.active .price-btn-range {
		color: var(--blue);
	}

	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0,0,0,0.3);
		z-index: 100;
	}
	.modal {
		position: fixed;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		background: var(--bg-card);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		z-index: 110;
		padding: 24px;
		width: 360px;
		max-width: 90vw;
	}
	.modal h3 {
		font-size: 18px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0 0 16px;
	}
	.modal-fields {
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-bottom: 20px;
	}
	.modal-fields label {
		display: flex;
		flex-direction: column;
		gap: 4px;
		font-size: 13px;
		font-weight: 500;
		color: var(--text-dark);
	}
	.modal-fields input {
		padding: 10px 12px;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		font-size: 14px;
		font-family: inherit;
		outline: none;
	}
	.modal-fields input:focus {
		border-color: var(--blue);
		box-shadow: 0 0 0 2px rgba(59,130,246,0.15);
	}
	.modal-actions {
		display: flex;
		gap: 8px;
	}
	.modal-actions button {
		flex: 1;
		padding: 10px;
		border: none;
		border-radius: var(--radius-md);
		font-size: 14px;
		font-weight: 600;
		cursor: pointer;
		font-family: inherit;
		transition: background 0.15s;
	}
	.btn-apply {
		background: var(--blue);
		color: var(--text-white);
	}
	.btn-apply:hover {
		background: #2563eb;
	}
	.btn-clear {
		background: var(--bg-hover);
		color: var(--text-dark);
	}
	.btn-clear:hover {
		background: var(--border);
	}
	.btn-cancel {
		background: transparent;
		color: var(--text-muted);
	}
	.btn-cancel:hover {
		background: var(--bg-muted);
	}

	.pills {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 20px;
		align-items: center;
	}
	.pill {
		padding: 5px 12px;
		border: 1px solid var(--border);
		border-radius: 20px;
		background: var(--bg-card);
		font-size: 12px;
		color: var(--text-dark);
		cursor: pointer;
		font-family: inherit;
		transition: all 0.15s;
	}
	.pill:hover {
		border-color: var(--blue);
		color: var(--blue);
	}
	.pill.active {
		background: var(--blue);
		color: var(--text-white);
		border-color: var(--blue);
	}
	.pill-sep {
		width: 1px;
		height: 20px;
		background: var(--border);
		margin: 0 4px;
	}

	.loading, .empty {
		padding: 48px 0;
		text-align: center;
		color: var(--text-muted);
		font-size: 14px;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
		gap: 16px;
	}
	.card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		overflow: hidden;
		cursor: pointer;
		text-align: left;
		font-family: inherit;
		font-size: inherit;
		padding: 0;
		transition: box-shadow 0.2s;
	}
	.card:hover {
		box-shadow: 0 4px 14px rgba(0,0,0,0.08);
	}
	.card-img {
		height: 180px;
		background: var(--bg-hover);
		overflow: hidden;
	}
	.card-img img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	.no-photo {
		height: 180px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--text-muted);
		font-size: 13px;
		background: var(--bg-hover);
	}
	.card-body {
		padding: 12px 14px;
	}
	.card-title {
		font-size: 15px;
		font-weight: 600;
		color: var(--text-dark);
		margin-bottom: 2px;
	}
	.card-sub {
		font-size: 12px;
		color: var(--text-muted);
		margin-bottom: 6px;
	}
	.card-price {
		font-size: 16px;
		font-weight: 700;
		color: var(--blue-dark);
		margin-bottom: 6px;
	}
	.card-specs {
		display: flex;
		gap: 6px;
		flex-wrap: wrap;
	}
	.card-specs span {
		font-size: 11px;
		background: var(--bg-hover);
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		color: var(--text-light);
		text-transform: capitalize;
	}
</style>
