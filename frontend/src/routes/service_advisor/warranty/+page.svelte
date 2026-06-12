<script lang="ts">
	import { onMount } from 'svelte';
	import { getServiceAdvisorWarranty } from '$lib/services/api';
	import DataTable from '$lib/components/DataTable.svelte';

	let claims = $state<Record<string, unknown>[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await getServiceAdvisorWarranty();
			claims = res.data as Record<string, unknown>[];
		} catch {
			// error
		} finally {
			loading = false;
		}
	});
</script>

<h1>Warranty Claims</h1>

{#if loading}
	<p>Loading…</p>
{:else if claims.length > 0}
	<DataTable columns={['ID', 'Customer', 'Vehicle', 'Type', 'Status', 'Submitted']}>
		{#each claims as c}
			<tr>
				<td>{c.claim_id}</td>
				<td>{c.customer_name ?? '—'}</td>
				<td>{(c.brand ?? '') + ' ' + (c.model ?? '')}</td>
				<td>{c.claim_type ?? '—'}</td>
				<td>{c.status ?? '—'}</td>
				<td>{c.submitted_at ? String(c.submitted_at).slice(0, 10) : '—'}</td>
			</tr>
		{/each}
	</DataTable>
{:else}
	<p>No warranty claims.</p>
{/if}

<style>
	h1 { padding: 1.5rem 1.5rem 0; margin: 0; }
</style>
