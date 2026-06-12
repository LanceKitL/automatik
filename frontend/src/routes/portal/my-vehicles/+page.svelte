<script lang="ts">
	import { onMount } from 'svelte';
	import { getCustomerDashboard } from '$lib/services/api';
	import { Car, Gauge, Fuel, Hash } from '@lucide/svelte';
	import Loader from '$lib/components/Loader.svelte';

	let vehicles = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getCustomerDashboard();
			vehicles = res.data?.dashboard?.my_vehicles ?? [];
		} catch {
			// ignore
		} finally {
			loading = false;
		}
	});
</script>

<div class="page-header">
	<h1>My Vehicles</h1>
	<p class="subtitle">View and manage your registered vehicles.</p>
</div>

{#if loading}
	<div class="loader"><Loader /></div>
{:else if vehicles.length === 0}
	<div class="empty">No vehicles found. Purchase a vehicle to see it here.</div>
{:else}
	<div class="vehicle-list">
		{#each vehicles as v}
			<div class="vehicle-card">
				<div class="card-top">
					<div class="vehicle-icon">
						<Car size={40} />
					</div>
					<div class="vehicle-info">
						<div class="vehicle-name">{v.brand ?? '—'} {v.model ?? '—'}</div>
						<div class="vehicle-meta">
							<span class="meta-chip"><Gauge size={12} /> {(v.mileage ?? '—') as string}</span>
							<span class="meta-chip"><Fuel size={12} /> {(v.fuel_type ?? '—') as string}</span>
							<span class="meta-chip"><Hash size={12} /> {(v.license_plate ?? '—') as string}</span>
						</div>
					</div>
					<span class="status-dot status-green"></span>
				</div>
				<div class="card-body">
					<div class="detail-row">
						<span class="label">Year</span>
						<span class="value">{v.year ?? '—'}</span>
					</div>
					<div class="detail-row">
						<span class="label">Color</span>
						<span class="value">{v.color ?? '—'}</span>
					</div>
					<div class="detail-row">
						<span class="label">VIN</span>
						<span class="value vin">{(v.vin ?? '—') as string}</span>
					</div>
				</div>
			</div>
		{/each}
	</div>
{/if}

<style>
	.page-header {
		margin-bottom: 24px;
	}
	h1 {
		font-size: 24px;
		font-weight: 700;
		color: var(--text-dark);
		margin: 0;
	}
	.subtitle {
		font-size: 14px;
		color: var(--text-muted);
		margin-top: 4px;
	}
	.loader {
		display: grid;
		place-items: center;
		height: 50vh;
	}
	.empty {
		text-align: center;
		padding: 60px 20px;
		color: var(--text-muted);
		font-size: 14px;
	}
	.vehicle-list {
		display: flex;
		flex-direction: column;
		gap: 16px;
	}
	.vehicle-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		overflow: hidden;
		box-shadow: var(--shadow-sm);
	}
	.card-top {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 16px 20px;
		background: var(--bg-muted);
		border-bottom: 1px solid var(--border);
	}
	.vehicle-icon {
		width: 64px;
		height: 64px;
		background: var(--primary-bg);
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--primary);
		flex-shrink: 0;
	}
	.vehicle-info {
		flex: 1;
	}
	.vehicle-name {
		font-size: 16px;
		font-weight: 700;
		color: var(--text-dark);
		margin-bottom: 6px;
	}
	.vehicle-meta {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}
	.meta-chip {
		display: inline-flex;
		align-items: center;
		gap: 4px;
		font-size: 11px;
		color: var(--text-light);
		background: var(--bg-card);
		padding: 3px 8px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
	}
	.status-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		flex-shrink: 0;
	}
	.status-dot.status-green {
		background: #22c55e;
	}
	.card-body {
		padding: 16px 20px;
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
	}
	.detail-row {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}
	.label {
		font-size: 11px;
		color: var(--text-muted);
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}
	.value {
		font-size: 13px;
		font-weight: 600;
		color: var(--text-dark);
	}
	.value.vin {
		font-family: monospace;
		font-size: 11px;
	}
</style>
