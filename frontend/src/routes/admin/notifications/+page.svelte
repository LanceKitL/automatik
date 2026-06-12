<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getAdminNotifications, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'notification_id', label: 'ID' },
		{ key: 'title', label: 'Title' },
		{ key: 'message', label: 'Message' },
		{ key: 'is_read', label: 'Read' },
		{ key: 'created_at', label: 'Date' },
	];

	onMount(async () => {
		try {
			const res = await getAdminNotifications();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Notifications</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.notification_id)}
			<tr>
				<td>{row.notification_id}</td>
				<td>{row.title}</td>
				<td>{row.message}</td>
				<td>{row.is_read ? 'Yes' : 'No'}</td>
				<td>{row.created_at}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
