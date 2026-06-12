<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getPayments, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

    const columns = [
        { key: 'payment_id', label: 'ID' },
        { key: 'sale_id', label: 'Sale' },
        { key: 'amount_paid', label: 'Amount' },
        { key: 'payment_method', label: 'Method' },
        { key: 'payment_allocation', label: 'Allocation' },
        { key: 'payment_date', label: 'Date' },
    ];

	onMount(async () => {
		try {
			const res = await getPayments();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Payments</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.payment_id)}
			<tr>
				<td>{row.payment_id}</td>
				<td>{row.sale_id}</td>
                <td>{row.amount_paid}</td>
                <td>{row.payment_method}</td>
                <td>{row.payment_allocation ?? '—'}</td>
                <td>{row.payment_date}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
