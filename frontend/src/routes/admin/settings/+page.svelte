<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getSettings, type SettingsResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<{ setting_id: number; setting_key: string; setting_value: string; description: string | null }[]>([]);

	const columns = [
		{ key: 'setting_key', label: 'Key' },
		{ key: 'setting_value', label: 'Value' },
		{ key: 'description', label: 'Description' },
	];

	onMount(async () => {
		try {
			const res = await getSettings();
			rows = Object.values(res.data);
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<h1>Settings</h1>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.setting_id)}
			<tr>
				<td>{row.setting_key}</td>
				<td>{row.setting_value}</td>
				<td>{row.description}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
