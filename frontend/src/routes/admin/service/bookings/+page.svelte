<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getServiceBookings, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'booking_id', label: 'ID' },
		{ key: 'customer_id', label: 'Customer' },
		{ key: 'vehicle_id', label: 'Vehicle' },
		{ key: 'booking_type', label: 'Type' },
		{ key: 'status', label: 'Status' },
		{ key: 'slot_id', label: 'Slot' },
	];

	onMount(async () => {
		try {
			const res = await getServiceBookings();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Service Bookings</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.booking_id)}
			<tr>
				<td>{row.booking_id}</td>
				<td>{row.customer_id}</td>
				<td>{row.vehicle_id}</td>
				<td>{row.booking_type}</td>
				<td>{row.status}</td>
				<td>{row.slot_id}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
