<script lang="ts">
	import { onMount } from 'svelte';
	import DataTable from '$lib/components/DataTable.svelte';
	import { getLoans, type ListResponse } from '$lib/services/api';

	let loading = $state(true);
	let error = $state<string | null>(null);
	let rows = $state<unknown[]>([]);

	const columns = [
		{ key: 'loan_id', label: 'ID' },
		{ key: 'sale_id', label: 'Sale' },
		{ key: 'loan_amount', label: 'Amount' },
		{ key: 'interest_rate', label: 'Rate' },
		{ key: 'term_months', label: 'Term (mo)' },
		{ key: 'bank_approval_status', label: 'Status' },
	];

	onMount(async () => {
		try {
			const res = await getLoans();
			rows = res.data;
		} catch (e) {
			error = (e as Error).message;
		} finally {
			loading = false;
		}
	});
</script>

<div class="page">
<div class="title-row">
	<div>
		<h1>Loans</h1>
		<p class="title-subtitle">View and manage customer loan applications</p>
	</div>
</div>
{#if loading}
	<p>Loading…</p>
{:else if error}
	<p class="error">{error}</p>
{:else}
	<DataTable {columns}>
		{#each rows as row (row.loan_id)}
			<tr>
				<td>{row.loan_id}</td>
				<td>{row.sale_id}</td>
				<td>{row.loan_amount}</td>
				<td>{row.interest_rate}</td>
				<td>{row.term_months}</td>
				<td>{row.bank_approval_status}</td>
			</tr>
		{/each}
	</DataTable>
{/if}
</div>

<style>
	.page { padding: 2rem 1.5rem; max-width: 1200px; margin: 0 auto; font-family: var(--font-sans); }
	.title-row { display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem; }
	.title-subtitle { font-size: 13px; color: #9ca3af; margin: 2px 0 0; font-weight: 400; }
	h1 { font-size: 24px; font-weight: 700; color: #1a1a2e; margin: 0; }
	.error { color: #dc2626; font-size: 13px; }
</style>
