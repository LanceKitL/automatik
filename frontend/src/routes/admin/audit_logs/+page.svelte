<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getAuditLogs, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'log_id', label: 'ID' },
		{ key: 'user_id', label: 'User' },
		{ key: 'action', label: 'Action' },
		{ key: 'table_name', label: 'Table' },
		{ key: 'record_id', label: 'Record' },
		{ key: 'created_at', label: 'Timestamp' },
	];

	onMount(async () => {
		try {
			const res = await getAuditLogs();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Audit Log</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.log_id)}
			<tr>
				<td>{row.log_id}</td>
				<td>{row.user_id}</td>
				<td>{row.action}</td>
				<td>{row.table_name}</td>
				<td>{row.record_id}</td>
				<td>{row.created_at}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
