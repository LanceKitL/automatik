<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getCommissions } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	let columns = $state<{ key: string; label: string }[]>([]);

	onMount(async () => {
		try {
			const res = await getCommissions();
			rows = res;
			if (res.length > 0) {
				columns = Object.keys(res[0]).map((k) => ({ key: k, label: k.replace(/_/g, ' ') }));
			}
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Commissions</h1>
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
