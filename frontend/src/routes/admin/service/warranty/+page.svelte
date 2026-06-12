<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getAdminWarrantyClaims, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'claim_id', label: 'ID' },
		{ key: 'sale_id', label: 'Sale' },
		{ key: 'claim_type', label: 'Type' },
		{ key: 'status', label: 'Status' },
		{ key: 'submitted_at', label: 'Submitted' },
	];

	onMount(async () => {
		try {
			const res = await getAdminWarrantyClaims();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Warranty Claims</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.claim_id)}
			<tr>
				<td>{row.claim_id}</td>
				<td>{row.sale_id}</td>
				<td>{row.claim_type}</td>
				<td>{row.status}</td>
				<td>{row.submitted_at}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
