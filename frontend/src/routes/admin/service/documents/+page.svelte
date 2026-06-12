<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getAdminDocuments } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'document_id', label: 'ID' },
		{ key: 'sale_id', label: 'Sale' },
		{ key: 'document_type', label: 'Type' },
		{ key: 'file_url', label: 'File' },
		{ key: 'created_at', label: 'Uploaded' },
	];

	onMount(async () => {
		try {
			const res = await getAdminDocuments();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Documents</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row, i (i)}
			<tr>
				{#each columns as col}
					<td>{row[col.key]}</td>
				{/each}
			</tr>
		{/each}
	</DataTable>
{/if}
